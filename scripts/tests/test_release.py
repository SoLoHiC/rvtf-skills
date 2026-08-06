import json
import tempfile
import unittest
from pathlib import Path
import tarfile
from typing import Optional

from release import ReleaseError, audit_package, check_version, extract_changelog, main, set_version


class ReleaseHelperTests(unittest.TestCase):
    def make_project(self, version: str = "0.4.0", changelog: Optional[str] = None) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
        (root / "package.json").write_text(
            json.dumps({"name": "rvtf-skills", "version": version, "license": "MIT"}) + "\n",
            encoding="utf-8",
        )
        (root / "CHANGELOG.md").write_text(
            changelog or "# Changelog\n\n## [0.4.0] - 2026-08-06\n\n- Initial release.\n\n## [0.3.0] - 2026-07-01\n\n- Legacy.\n",
            encoding="utf-8",
        )
        return root

    def make_archive(
        self,
        root: Path,
        version: str = "0.4.0",
        unsafe_name: Optional[str] = None,
        forbidden_name: Optional[str] = None,
    ) -> Path:
        package = root / "package"
        package.mkdir()
        (package / "VERSION").write_text(f"{version}\n", encoding="utf-8")
        (package / "package.json").write_text(
            json.dumps({"name": "rvtf-skills", "version": version, "license": "MIT"}) + "\n",
            encoding="utf-8",
        )
        (package / "LICENSE").write_text("MIT\n", encoding="utf-8")
        (package / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
        (package / "THIRD_PARTY_NOTICES.md").write_text("Notices\n", encoding="utf-8")
        skills = package / "skills"
        for name in ["one", "two", "three", "four", "five"]:
            skill = skills / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: sample\ndescription: sample\n---\n", encoding="utf-8")
        archive = root / "archive.tgz"
        with tarfile.open(archive, "w:gz") as handle:
            handle.add(package, arcname="package")
            if unsafe_name:
                info = tarfile.TarInfo(unsafe_name)
                info.size = 0
                handle.addfile(info)
            if forbidden_name:
                info = tarfile.TarInfo(forbidden_name)
                info.size = 0
                handle.addfile(info)
        return archive

    def test_validates_version_and_detects_mismatch(self) -> None:
        root = self.make_project()
        check_version(root, "0.4.0")
        self.assertEqual(main(["--root", str(root), "version", "--check", "0.4.0"]), 0)
        with self.assertRaisesRegex(ReleaseError, "strict X.Y.Z"):
            check_version(root, "v0.4.0")
        with self.assertRaisesRegex(ReleaseError, "does not match"):
            check_version(self.make_project("0.4.1"), "0.4.0")

    def test_sets_only_project_version_sources(self) -> None:
        root = self.make_project()
        set_version(root, "0.4.1")
        self.assertEqual((root / "VERSION").read_text().strip(), "0.4.1")
        self.assertEqual(json.loads((root / "package.json").read_text())["version"], "0.4.1")

    def test_extracts_one_changelog_section(self) -> None:
        root = self.make_project()
        self.assertEqual(extract_changelog(root, "0.4.0"), "## [0.4.0] - 2026-08-06\n\n- Initial release.")
        with self.assertRaisesRegex(ReleaseError, "No CHANGELOG section"):
            extract_changelog(self.make_project(changelog="# Changelog\n"), "0.4.0")

    def test_audits_archive_identity_and_required_files(self) -> None:
        root = self.make_project()
        archive = self.make_archive(root)
        audit_package(archive, "0.4.0")
        with self.assertRaisesRegex(ReleaseError, "safe archive path"):
            audit_package(self.make_archive(self.make_project(), unsafe_name="../escape"), "0.4.0")
        with self.assertRaisesRegex(ReleaseError, "forbidden test path"):
            audit_package(
                self.make_archive(self.make_project(), forbidden_name="package/scripts/tests/test.py"),
                "0.4.0",
            )


if __name__ == "__main__":
    unittest.main()
