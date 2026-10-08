import unittest
from pathlib import Path
from ag_mode.security.sanitizer import sanitize_text, is_safe_path


class TestSecuritySanitizer(unittest.TestCase):
    def test_gemini_key_redacted(self):
        # Sample fake Gemini key (starts with AIza + 35 chars)
        fake_gemini_key = "AIzaSyD-fakeKeyExample1234567890ABCDEF"
        text = f"Using API key {fake_gemini_key} for testing"
        sanitized = sanitize_text(text)
        self.assertNotIn(fake_gemini_key, sanitized)
        self.assertIn("[REDACTED_GEMINI_API_KEY]", sanitized)

    def test_openai_key_redacted(self):
        fake_openai_key = "sk-abcdefghijklmnopqrstuvwxyz123456"
        text = f"Header: Authorization: Bearer {fake_openai_key}"
        sanitized = sanitize_text(text)
        self.assertNotIn(fake_openai_key, sanitized)

    def test_database_password_redacted(self):
        conn_str = "postgres://admin:SecretPassword123@localhost:5432/db"
        sanitized = sanitize_text(conn_str)
        self.assertNotIn("SecretPassword123", sanitized)
        self.assertIn("://***:***@", sanitized)

    def test_safe_path_boundaries(self):
        workspace = Path("/tmp/mock_workspace")
        # Allowed path inside workspace
        child_path = workspace / ".agents" / "rules" / "ag_active_mode.md"
        self.assertTrue(is_safe_path(child_path, [workspace]))

        # Disallowed protected system directory
        system_path = Path("C:/Windows/System32/drivers/etc/hosts")
        self.assertFalse(is_safe_path(system_path, [workspace]))


if __name__ == "__main__":
    unittest.main()
