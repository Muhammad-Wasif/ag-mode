import unittest
from ag_mode.core.registry import mode_registry
from ag_mode.core.resolver import DependencyResolver


class TestDependencyResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = DependencyResolver(mode_registry)

    def test_resolve_independent_mode(self):
        resolved = self.resolver.resolve("web")
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].id, "web")

    def test_resolve_mode_with_dependencies(self):
        # fullstack depends on frontend and backend
        resolved = self.resolver.resolve("fullstack")
        resolved_ids = [m.id for m in resolved]
        self.assertIn("frontend", resolved_ids)
        self.assertIn("backend", resolved_ids)
        self.assertIn("fullstack", resolved_ids)
        # Root mode should be last in topological order
        self.assertEqual(resolved_ids[-1], "fullstack")

    def test_collect_all_files_deduplication(self):
        resolved = self.resolver.resolve("fullstack")
        files = self.resolver.collect_all_files(resolved)
        self.assertTrue(len(files) > 0)
        # Ensure no duplicate (mode.id, filename) pairs
        keys = [f"{m.id}:{f}" for m, f in files]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
