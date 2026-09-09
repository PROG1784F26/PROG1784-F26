"""Check the real devcontainer environment as the vscode user, without model pulls."""

import json
import os
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
venv = Path("/home/vscode/.venv")
assert Path(sys.prefix) == venv, f"Wrong Python environment: {sys.prefix}"
assert os.getuid() != 0, "Run this check as vscode"
assert os.access(venv, os.W_OK), "Virtual environment is not writable"
with tempfile.TemporaryFile(dir=root) as handle:
    handle.write(b"Workspace writes work")
assert (Path.home() / ".continue/config.yaml").read_bytes() == (
    root / ".continue/config.yaml"
).read_bytes(), "Continue configuration has not been installed"
api = os.environ.get("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
with urlopen(f"{api}/api/version", timeout=10) as response:
    print("Ollama:", json.load(response)["version"])
with urlopen("http://127.0.0.1:11435/health", timeout=10) as response:
    assert json.load(response)["status"] == "ok"
for mode in ["tutor", "direct"]:
    with urlopen(f"http://127.0.0.1:11435/{mode}/api/version", timeout=10) as response:
        assert json.load(response)["version"]
print(
    "Python environment, workspace writes, Continue config, tutor adapter, and Ollama network: OK"
)
