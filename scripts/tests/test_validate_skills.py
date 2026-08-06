import tempfile
import unittest
from pathlib import Path

from validate_skills import validate_skill


class ValidateSkillTests(unittest.TestCase):
    def make_skill(self, frontmatter: str = "name: sample-skill\ndescription: A valid skill.") -> Path:
        root = Path(tempfile.mkdtemp())
        skill = root / "sample-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n# Sample\n", encoding="utf-8")
        return skill

    def assert_invalid(self, frontmatter: str, message: str) -> None:
        valid, detail = validate_skill(self.make_skill(frontmatter))
        self.assertFalse(valid)
        self.assertIn(message, detail)

    def test_accepts_valid_skill(self) -> None:
        valid, detail = validate_skill(self.make_skill())
        self.assertTrue(valid)
        self.assertIn("valid", detail.lower())

    def test_rejects_missing_skill_file(self) -> None:
        root = Path(tempfile.mkdtemp()) / "missing"
        root.mkdir()
        valid, detail = validate_skill(root)
        self.assertFalse(valid)
        self.assertIn("SKILL.md", detail)

    def test_rejects_missing_frontmatter(self) -> None:
        root = Path(tempfile.mkdtemp()) / "plain"
        root.mkdir()
        (root / "SKILL.md").write_text("# Plain\n", encoding="utf-8")
        valid, detail = validate_skill(root)
        self.assertFalse(valid)
        self.assertIn("frontmatter", detail.lower())

    def test_rejects_unexpected_key(self) -> None:
        self.assert_invalid("name: sample-skill\ndescription: ok\nowner: team", "Unexpected")

    def test_rejects_missing_required_fields(self) -> None:
        self.assert_invalid("description: ok", "Missing 'name'")
        self.assert_invalid("name: sample-skill", "Missing 'description'")

    def test_rejects_invalid_name(self) -> None:
        self.assert_invalid("name: Sample Skill\ndescription: ok", "hyphen-case")
        self.assert_invalid("name: -sample\ndescription: ok", "start/end")

    def test_rejects_long_name(self) -> None:
        self.assert_invalid(f"name: {'a' * 65}\ndescription: ok", "too long")

    def test_rejects_invalid_description(self) -> None:
        self.assert_invalid("name: sample-skill\ndescription: 42", "string")
        self.assert_invalid("name: sample-skill\ndescription: '<unsafe>'", "angle brackets")
        self.assert_invalid(f"name: sample-skill\ndescription: {'a' * 1025}", "too long")


if __name__ == "__main__":
    unittest.main()
