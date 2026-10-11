"""Focused path-safety checks for the community asset validator."""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("validate_catalogue.py")
SPEC = importlib.util.spec_from_file_location("validate_catalogue", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class RepositoryPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.old_root = validator.ROOT
        validator.ROOT = Path(self.temp.name)

    def tearDown(self) -> None:
        validator.ROOT = self.old_root
        self.temp.cleanup()

    def test_accepts_only_direct_files_inside_package_version(self) -> None:
        target = validator.ROOT / "packages/alice/demo/1.0.0/clip.mp4"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"video")
        path, extension = validator.repo_file("packages/alice/demo/1.0.0/clip.mp4", "packages/alice/demo/1.0.0")
        self.assertEqual(path, target)
        self.assertEqual(extension, "mp4")

    def test_rejects_traversal_and_nested_paths(self) -> None:
        with self.assertRaises(ValueError):
            validator.repo_file("packages/alice/demo/1.0.0/../clip.mp4", "packages/alice/demo/1.0.0")
        with self.assertRaises(ValueError):
            validator.repo_file("packages/alice/demo/1.0.0/sub/clip.mp4", "packages/alice/demo/1.0.0")

    def test_rejects_symlinked_package_components(self) -> None:
        packages = validator.ROOT / "packages"
        packages.mkdir()
        outside = validator.ROOT / "outside"
        outside.mkdir()
        try:
            (packages / "alice").symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink creation is unavailable: {error}")
        with self.assertRaises(ValueError):
            validator.repo_file("packages/alice/demo/1.0.0/clip.mp4", "packages/alice/demo/1.0.0")


if __name__ == "__main__":
    unittest.main()
