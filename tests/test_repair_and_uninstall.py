import tempfile
import unittest
from pathlib import Path

from ag_mode.config import get_config_path
from ag_mode.installer.repair import repair
from ag_mode.installer.uninstaller import uninstall
from ag_mode.integration.adapter import AntiGravityAdapter


class TestRepairAndUninstall(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ws_root = Path(self.temp_dir.name)
        # Create a user file
        self.user_file = self.ws_root / "important_project_data.json"
        self.user_file.write_text('{"user_data": true}', encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_repair_corrupted_config(self):
        cfg_path = get_config_path()
        # Corrupt config with invalid JSON
        cfg_path.write_text("NOT_VALID_JSON{::: broken", encoding="utf-8")

        res = repair(self.ws_root)
        self.assertTrue(res["success"])
        # Verify config is now valid JSON
        import json
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("theme", data)

    def test_uninstall_preserves_user_files(self):
        # First activate a mode
        adapter = AntiGravityAdapter(self.ws_root)
        adapter.activate_mode("web")

        # Now run uninstall on workspace
        res = uninstall(workspace_root=self.ws_root, remove_all_appdata=False)
        self.assertTrue(res["success"])

        # Check AG Mode rules removed
        self.assertFalse((self.ws_root / ".agents" / "rules" / "ag_active_mode.md").exists())

        # Check user project file is preserved
        self.assertTrue(self.user_file.exists())
        self.assertEqual(self.user_file.read_text(encoding="utf-8"), '{"user_data": true}')


if __name__ == "__main__":
    unittest.main()
