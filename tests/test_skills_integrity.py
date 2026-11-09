import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestSkillsIntegrity(unittest.TestCase):
    def test_required_files_and_frontmatter(self):
        self.assertTrue((ROOT / "AGENTS.md").exists())
        self.assertTrue((ROOT / "README.md").exists())
        for skill_name in ("toefl-vocab", "toefl-speaking", "toefl-writing"):
            skill_path = ROOT / ".agents" / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill_path.exists(), f"Missing {skill_path}")
            text = skill_path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\nname: " + skill_name))
            self.assertIn("my_weakness_log.json", text)


if __name__ == "__main__":
    unittest.main()
