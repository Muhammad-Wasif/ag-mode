import tempfile
import unittest
from pathlib import Path

from ag_mode.config import ActiveModeState
from ag_mode.integration.adapter import AntiGravityAdapter
from ag_mode.integration.backup import backup_manager


class TestAdapterLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ws_root = Path(self.temp_dir.name)
        # Create a mock user file that should never be touched or deleted
        self.user_file = self.ws_root / "src" / "index.js"
        self.user_file.parent.mkdir(parents=True, exist_ok=True)
        self.user_file.write_text("console.log('User existing code');", encoding="utf-8")
        self.adapter = AntiGravityAdapter(self.ws_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_full_activation_switching_and_deactivation_cycle(self):
        # 1. Activate Web Development Mode
        res = self.adapter.activate_mode("web")
        self.assertTrue(res["success"], f"Activation failed: {res.get('error')}")

        # Verify generated files
        self.assertTrue((self.ws_root / ".agents" / "rules" / "ag_active_mode.md").exists())
        self.assertTrue((self.ws_root / ".agents" / "rules" / "ag_quality_gate.md").exists())
        self.assertTrue((self.ws_root / ".agents" / "rules" / "ag_tools.md").exists())
        self.assertTrue((self.ws_root / "GEMINI.md").exists())

        # Verify active state
        state = ActiveModeState.load(self.ws_root)
        self.assertIsNotNone(state)
        self.assertEqual(state.mode_id, "web")

        # Verify user code is intact
        self.assertEqual(self.user_file.read_text(encoding="utf-8"), "console.log('User existing code');")

        # 2. Switch mode to Data Science
        res2 = self.adapter.activate_mode("data-science")
        self.assertTrue(res2["success"])
        state2 = ActiveModeState.load(self.ws_root)
        self.assertEqual(state2.mode_id, "data-science")

        # 3. Rollback to Web Development snapshot
        rollback_ok = backup_manager.rollback()
        self.assertTrue(rollback_ok)
        state_after_rollback = ActiveModeState.load(self.ws_root)
        self.assertEqual(state_after_rollback.mode_id, "web")

        # 4. Deactivate mode cleanly
        deact_ok = self.adapter.deactivate_mode()
        self.assertTrue(deact_ok)
        self.assertFalse((self.ws_root / ".agents" / "rules" / "ag_active_mode.md").exists())
        self.assertIsNone(ActiveModeState.load(self.ws_root))

        # Verify user code is still completely untouched
        self.assertTrue(self.user_file.exists())
        self.assertEqual(self.user_file.read_text(encoding="utf-8"), "console.log('User existing code');")


if __name__ == "__main__":
    unittest.main()
