"""Run inside a probe container to generate engine-specific Compose settings."""

import json
import os
from pathlib import Path


def runtime_override(is_podman, uid_map):
    # Podman rootless maps container root to one host UID. Docker must never
    # receive keep-id, because it does not implement that user namespace mode.
    first_mapping = uid_map.splitlines()[0].split()
    rootless = first_mapping[2] == "1"
    options = {"userns_mode": "keep-id"} if is_podman and rootless else {}
    return {"services": {"python": options}}


def main():
    is_podman = Path("/run/.containerenv").exists()
    override = runtime_override(is_podman, Path("/proc/self/uid_map").read_text())
    directory = Path("/config")
    destination = directory / "compose.runtime.yaml"
    destination.write_text(json.dumps(override, indent=2) + "\n")
    owner = directory.stat()
    os.chown(destination, owner.st_uid, owner.st_gid)
    print(f"Configured {'Podman' if is_podman else 'Docker'}: {override}")


if __name__ == "__main__":
    main()
