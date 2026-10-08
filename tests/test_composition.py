import unittest
from ag_mode.core.composer import ModeComposer
from ag_mode.core.registry import mode_registry


class TestModeComposer(unittest.TestCase):
    def setUp(self):
        self.composer = ModeComposer(mode_registry)

    def test_compose_web_and_cybersecurity(self):
        composed = self.composer.compose(["web", "cybersecurity"])
        self.assertEqual(composed.primary_mode_id, "web")
        self.assertIn("Web Development", composed.combined_name)
        self.assertIn("Cybersecurity", composed.combined_name)

        # Verify quality gates are merged and deduplicated
        self.assertGreater(len(composed.merged_quality_gates), 0)
        self.assertEqual(
            len(composed.merged_quality_gates),
            len(set(composed.merged_quality_gates)),
        )

    def test_compose_data_science_and_ml(self):
        composed = self.composer.compose(["data-science", "machine-learning"])
        resolved_ids = [m.id for m in composed.resolved_modes]
        self.assertIn("data-science", resolved_ids)
        self.assertIn("machine-learning", resolved_ids)


if __name__ == "__main__":
    unittest.main()
