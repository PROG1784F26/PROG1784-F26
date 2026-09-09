"""Measure cold/warm local inference; does not grade answers or execute model code."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

PROMPT = (
    "Explain Python for loops to a beginner in about 100 words, with one short example."
)


def api_json(base, endpoint, data=None):
    request = Request(
        base + endpoint,
        data=json.dumps(data).encode() if data is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=600) as response:
        return json.load(response)


def measure(base, model, cpu, context):
    options = {
        "num_ctx": context,
        "num_predict": 256,
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 40,
        "presence_penalty": 0,
        "seed": 42,
    }
    if cpu:
        options["num_gpu"] = 0
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": True,
        "think": False,
        "keep_alive": 300,
        "options": options,
    }
    request = Request(
        base + "/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.monotonic()
    first_content = None
    content = []
    final = {}
    with urlopen(request, timeout=600) as response:
        for line in response:
            chunk = json.loads(line)
            if chunk.get("error"):
                raise RuntimeError(chunk["error"])
            text = chunk.get("message", {}).get("content", "")
            if text:
                if first_content is None:
                    first_content = time.monotonic() - started
                content.append(text)
            if chunk.get("done"):
                final = chunk
    elapsed = time.monotonic() - started
    if not final:
        raise RuntimeError("Stream ended without completion")
    loaded = api_json(base, "/api/ps")["models"]
    loaded = next((item for item in loaded if item["name"] == model), None)
    generation = final.get("eval_duration", 0) / 1e9
    return {
        "seconds": round(elapsed, 3),
        "first_content_seconds": round(first_content, 3)
        if first_content is not None
        else None,
        "load_seconds": final.get("load_duration", 0) / 1e9,
        "prefill_seconds": final.get("prompt_eval_duration", 0) / 1e9,
        "generation_seconds": generation,
        "prompt_tokens": final.get("prompt_eval_count"),
        "output_tokens": final.get("eval_count"),
        "tokens_per_second": final.get("eval_count", 0) / generation
        if generation
        else None,
        "done_reason": final.get("done_reason"),
        "loaded": loaded,
        "options": options,
        "content": "".join(content),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default="http://ollama:11434")
    parser.add_argument("--model", action="append", required=True)
    parser.add_argument(
        "--cpu", action="store_true", help="Explicitly disable GPU offload"
    )
    parser.add_argument("--context", type=int, default=16384)
    parser.add_argument(
        "--repeat", type=int, default=3, help="One cold load followed by warm requests"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.context < 1024 or args.repeat < 1:
        parser.error("context must be >=1024 and repeat >=1")
    base = args.api_base.rstrip("/")
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "api_base": base,
        "cpu_requested": args.cpu,
        "server": api_json(base, "/api/version"),
        "prompt": PROMPT,
        "scope": "One model unload/load, then warm repeated prompts; OS disk cache not cleared. Not a quality benchmark.",
        "results": [],
    }
    tags = {model["name"]: model for model in api_json(base, "/api/tags")["models"]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    failed = False
    for model in args.model:
        entry = {"model": model, "metadata": tags.get(model), "requests": []}
        report["results"].append(entry)
        try:
            entry["details"] = api_json(base, "/api/show", {"model": model}).get(
                "details"
            )
            api_json(base, "/api/generate", {"model": model, "keep_alive": 0})
            for repetition in range(args.repeat):
                result = measure(base, model, args.cpu, args.context)
                result["phase"] = "cold_model_load" if repetition == 0 else "warm"
                entry["requests"].append(result)
                args.output.write_text(json.dumps(report, indent=2) + "\n")
                print(
                    f"{model} {result['phase']}: {result['seconds']}s, {result['tokens_per_second']:.1f} tokens/s",
                    flush=True,
                )
        except Exception as error:
            entry["error"] = f"{type(error).__name__}: {error}"
            failed = True
            print(f"{model}: {entry['error']}", flush=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
