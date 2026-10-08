import tempfile
import unittest
from pathlib import Path

from ag_mode.core.custom_mode import custom_mode_manager
from ag_mode.core.registry import mode_registry
from ag_mode.diagnostics.logger import logger
from ag_mode.integration.adapter import AntiGravityAdapter


class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ws = Path(self.temp_dir.name)
        self.adapter = AntiGravityAdapter(self.ws)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_invalid_mode_selection_fails_gracefully(self):
        res = self.adapter.activate_mode("completely_fake_nonexistent_mode_999")
        self.assertFalse(res["success"])
        self.assertIn("not found", res.get("error", "").lower())

    def test_custom_mode_lifecycle(self):
        custom_name = "Test University Robotics"
        mode = custom_mode_manager.create_mode(
            name=custom_name,
            description="Robotics engineering curriculum mode",
            category="Computer & Engineering",
        )
        self.assertEqual(mode.name, custom_name)
        self.assertEqual(mode.category, "Computer & Engineering")
        self.assertTrue(mode.is_custom)

        # Verify it can be activated in workspace
        res = self.adapter.activate_mode(mode.id)
        self.assertTrue(res["success"])

        # Delete custom mode
        deleted = custom_mode_manager.delete_custom_mode(mode.id)
        self.assertTrue(deleted)

    def test_web_mode_contains_anti_ai_and_logo_standards(self):
        web_mode = mode_registry.get("web")
        self.assertIsNotNone(web_mode)
        self.assertIn("anti-ai-patterns.md", web_mode.files)
        self.assertIn("logo-standards.md", web_mode.files)

        content = web_mode.load_file_content("anti-ai-patterns.md")
        self.assertIn("purple-to-blue gradients", content)
        self.assertIn("emoji", content)

    def test_islamic_mode_strict_source_control(self):
        islamic_mode = mode_registry.get("islamic-knowledge")
        self.assertIsNotNone(islamic_mode)
        self.assertIn("primary-sources.md", islamic_mode.files)

        content = islamic_mode.load_file_content("primary-sources.md")
        self.assertIn("The Holy Quran", content)
        self.assertIn("Sahih al-Bukhari", content)
        self.assertIn("Sahih Muslim", content)
        self.assertIn("Sunan Abu Dawud", content)
        self.assertIn("Jami' al-Tirmidhi", content)
        self.assertIn("Sunan al-Nasa'i", content)
        self.assertIn("Sunan Ibn Majah", content)

    def test_secrets_never_appear_in_logs(self):
        secret_token = "ghp_FakeGitHubPersonalAccessToken1234567890AB"
        logger.info("activation", f"Authenticated with token {secret_token}")
        recent = logger.get_recent_logs("activation", max_lines=5)
        last_log = "\n".join(recent)
        self.assertNotIn(secret_token, last_log)
        self.assertIn("[REDACTED_GITHUB_PAT]", last_log)


if __name__ == "__main__":
    unittest.main()
