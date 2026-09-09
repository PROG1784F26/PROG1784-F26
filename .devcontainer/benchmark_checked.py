"""Measure final checked-answer latency; run CPU/GPU servers sequentially."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gemma4:e4b-it-qat"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base", default="http://ollama:11434")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="200,201,202")
    args = parser.parse_args()

    def api(endpoint, body=None):
        request = Request(
            args.api_base.rstrip("/") + "/api/" + endpoint,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=270) as response:
            return json.load(response)

    metadata = {"version": api("version"), "tags": api("tags")}
    api("generate", {"model": MODEL, "keep_alive": 0, "stream": False})
    subprocess.run(
        [
            sys.executable,
            str(ROOT / ".devcontainer/optimize_gemma.py"),
            "--api-base",
            args.api_base,
            "--cases",
            str(ROOT / ".devcontainer/experiments/gemma_confirmation.json"),
            "--policy",
            str(ROOT / ".devcontainer/tutor_policy.yaml"),
            "--temperature",
            "1",
            "--seeds",
            args.seeds,
            "--checked",
            "--output",
            str(args.output),
        ],
        check=True,
    )
    metadata["loaded"] = api("ps")
    report = json.loads(args.output.read_text())
    report["runtime"] = metadata
    report["timing_notes"] = (
        "The first response starts after model unload; OS disk cache is not cleared. "
        "Subsequent responses are warm. Seconds include every generation and check, "
        "before any accepted answer is available; they exclude client/UI rendering. "
        "Inspect size_vram for actual GPU use. Run without competing inference. "
        "This is a small confirmation sample, not a new independent holdout."
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
