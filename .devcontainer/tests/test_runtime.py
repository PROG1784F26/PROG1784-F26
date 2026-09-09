"""Keep Podman-only settings out of Docker configurations."""

import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "configure_runtime", Path(__file__).resolve().parents[1] / "configure_runtime.py"
)
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class RuntimeTests(unittest.TestCase):
    def test_rootless_podman_preserves_host_identity(self):
        config = runtime.runtime_override(True, "0 1000 1\n1 100000 65536\n")
        self.assertEqual(config["services"]["python"]["userns_mode"], "keep-id")

    def test_docker_never_receives_podman_option(self):
        for uid_map in ("0 0 4294967295\n", "0 1000 1\n1 100000 65536\n"):
            config = runtime.runtime_override(False, uid_map)
            self.assertEqual(config["services"]["python"], {})

    def test_rootful_podman_uses_normal_mapping(self):
        config = runtime.runtime_override(True, "0 0 4294967295\n")
        self.assertEqual(config["services"]["python"], {})
