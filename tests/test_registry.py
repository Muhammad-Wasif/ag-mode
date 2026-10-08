import unittest
from ag_mode.core.registry import ModeRegistry, mode_registry


class TestModeRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = mode_registry
        self.registry.load_all()

    def test_registry_has_minimum_modes(self):
        # Must have at least 70 modes
        self.assertGreaterEqual(len(self.registry.modes), 70)

    def test_key_modes_exist(self):
        expected_modes = [
            "web", "frontend", "backend", "fullstack", "android", "ios",
            "data-science", "machine-learning", "deep-learning", "cybersecurity",
            "ethical-hacking", "computer-networks", "digital-logic",
            "windows-dev", "linux-dev", "islamic-knowledge", "mathematics",
        ]
        for mid in expected_modes:
            mode = self.registry.get(mid)
            self.assertIsNotNone(mode, f"Expected mode '{mid}' to be present in registry")
            self.assertTrue(len(mode.files) > 0, f"Mode '{mid}' should have files listed")

    def test_categories_presence(self):
        cats = self.registry.get_categories()
        required_cats = ["Development", "Data & AI", "Cybersecurity", "Computer & Engineering", "Academic & Study", "Languages & Writing", "General"]
        for rc in required_cats:
            self.assertIn(rc, cats)

    def test_dynamic_numbering(self):
        dev_modes = self.registry.get_numbered_modes("Development")
        self.assertGreater(len(dev_modes), 10)
        # Check numbering is sequential from 1
        numbers = [num for num, _ in dev_modes]
        self.assertEqual(numbers, list(range(1, len(dev_modes) + 1)))

    def test_search_functionality(self):
        # Search by tag
        py_results = self.registry.search("python")
        self.assertTrue(any(m.id == "data-science" for m in py_results))

        # Search by partial name
        web_results = self.registry.search("andro")
        self.assertTrue(any(m.id == "android" for m in web_results))

        # Search with no match
        empty_results = self.registry.search("nonexistent_random_token_xyz")
        self.assertEqual(len(empty_results), 0)


if __name__ == "__main__":
    unittest.main()
