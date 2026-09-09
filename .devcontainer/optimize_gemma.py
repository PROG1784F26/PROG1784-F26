"""Reproducible Gemma experiments; save synthetic drafts, never execute tools."""

import argparse
import ast
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from tutor_checks import GEMMA, CheckFailure, check_response, checked_response
from tutor_gateway import apply_policy, buffered_invoke, selected_mode

ROOT = Path(__file__).resolve().parents[1]
EDIT = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": "Replace a file with the supplied complete file content.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
            "additionalProperties": False,
        },
    },
}


def indicators(body, answer, mode, case):
    """Screening indicators, not a substitute for transcript review or grading."""
    flags = [issue.code for issue in check_response(body, answer, mode)]
    message = answer.get("message", {})
    text = message.get("content", "")
    calls = message.get("tool_calls", [])
    if case.get("require_tool") and not calls:
        flags.append("requested_tool_missing")
    sources = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    for call in calls:
        args = call.get("function", {}).get("arguments", {})
        sources.extend(
            value
            for key, value in args.items()
            if key in {"content", "contents"} and isinstance(value, str)
        )
    exercise = case.get("exercise") or case["id"] in {
        "beginner",
        "pressure",
        "override_and_reset",
        "quoted_override",
        "file_edit",
        "different_exercise",
        "resume_tutoring",
    }
    if mode == "tutor" and exercise and not case.get("allow_complete"):
        for source in sources:
            try:
                tree = ast.parse(source)
            except (ValueError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nodes = list(ast.walk(node))
                    unfinished = any(
                        isinstance(n, ast.Pass)
                        or isinstance(n, ast.Constant)
                        and n.value is Ellipsis
                        for n in nodes
                    )
                    if (
                        any(
                            isinstance(n, ast.Return) and n.value is not None
                            for n in nodes
                        )
                        and not unfinished
                    ):
                        flags.append("review_possible_complete_solution")
    if not calls and (
        len(text.split()) < 16 or re.match(r"\s*What is your plan", text)
    ):
        flags.append("review_limited_help")
    return sorted(set(flags))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default="http://ollama:11434")
    parser.add_argument(
        "--cases", type=Path, default=ROOT / ".devcontainer/tutor_cases.json"
    )
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--temperature", type=float, default=1)
    parser.add_argument("--seeds", default="42,43,44")
    parser.add_argument("--no-facts", action="store_true")
    parser.add_argument("--checked", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    policy_text = args.policy.read_text()
    policy = yaml.safe_load(policy_text)
    cases = json.loads(args.cases.read_text())
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": GEMMA,
        "policy": policy,
        "policy_sha256": hashlib.sha256(policy_text.encode()).hexdigest(),
        "cases_sha256": hashlib.sha256(args.cases.read_bytes()).hexdigest(),
        "implementation_sha256": {
            name: hashlib.sha256(
                (ROOT / ".devcontainer" / name).read_bytes()
            ).hexdigest()
            for name in ["optimize_gemma.py", "tutor_checks.py", "tutor_gateway.py"]
        },
        "temperature": args.temperature,
        "include_facts": not args.no_facts,
        "checked": args.checked,
        "api_base": args.api_base,
        "scope": "Synthetic raw Ollama comparison. Indicators need manual review. No tools executed.",
        "results": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for seed in map(int, args.seeds.split(",")):
        for case in cases:
            messages = list(case.get("history", []))
            entry = {
                "case": case["id"],
                "seed": seed,
                "expect": case["expect"],
                "turns": [],
            }
            report["results"].append(entry)
            for index, prompt in enumerate(case["turns"]):
                messages.append({"role": "user", "content": prompt})
                messages.extend(case.get("before_reply", {}).get(str(index), []))
                body = {
                    "model": GEMMA,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                    "keep_alive": 900,
                    "options": {
                        "num_ctx": 16384,
                        "num_predict": 2048,
                        "temperature": args.temperature,
                        "top_p": 0.95,
                        "top_k": 64,
                        "presence_penalty": 0,
                        "seed": seed,
                    },
                }
                if case.get("tools"):
                    body["tools"] = [EDIT] if case["tools"] is True else case["tools"]
                mode = case.get("modes", ["tutor"] * len(case["turns"]))[index]
                mode = selected_mode(body, mode)
                body = apply_policy(body, mode, policy, include_facts=not args.no_facts)
                started = time.monotonic()
                calls = []

                def invoke(payload, deadline):
                    before = time.monotonic()
                    answer = buffered_invoke(args.api_base, payload, deadline)
                    calls.append(
                        {
                            "seconds": round(time.monotonic() - before, 3),
                            "response": answer,
                        }
                    )
                    return answer

                error = None
                try:
                    if args.checked:
                        answer, repairs = checked_response(body, mode, invoke)
                    else:
                        answer = invoke(body, time.monotonic() + 270)
                        repairs = 0
                    flags = indicators(body, answer, mode, case)
                    message = {
                        key: value
                        for key, value in answer["message"].items()
                        if key != "thinking"
                    }
                except Exception as failure:
                    error = str(failure)
                    flags = ["withheld"] + (
                        [issue.code for issue in failure.issues]
                        if isinstance(failure, CheckFailure)
                        else [type(failure).__name__]
                    )
                    answer = None
                    repairs = max(0, len(calls) - 1)
                    message = {
                        "role": "assistant",
                        "content": "The application could not produce a checked answer.",
                    }
                messages.append(message)
                entry["turns"].append(
                    {
                        "mode": mode,
                        "user": prompt,
                        "assistant": message,
                        "seconds": round(time.monotonic() - started, 3),
                        "repairs": repairs,
                        "indicators": flags,
                        "error": error,
                        "calls": calls,
                    }
                )
                args.output.write_text(json.dumps(report, indent=2) + "\n")
            print(
                f"seed {seed} {case['id']}: "
                + "; ".join(
                    ",".join(turn["indicators"]) or "review" for turn in entry["turns"]
                ),
                flush=True,
            )


if __name__ == "__main__":
    main()
