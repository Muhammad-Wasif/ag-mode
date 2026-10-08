import unittest
from ag_mode.platform.detector import detect_platform, detect_architecture


class TestPlatformDetector(unittest.TestCase):
    def test_detect_platform_returns_valid_info(self):
        info = detect_platform()
        self.assertIn(info.os_name, ["Windows", "Linux", "Darwin"])
        self.assertIn(info.arch, ["x64", "arm64", "x86", "other", "aarch64", "amd64"])
        self.assertIsNotNone(info.python_version)
        self.assertIsNotNone(info.shell_name)

    def test_architecture_normalized(self):
        arch = detect_architecture()
        self.assertTrue(len(arch) > 0)


if __name__ == "__main__":
    unittest.main()
