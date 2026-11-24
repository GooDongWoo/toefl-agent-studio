import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestSkillsIntegrity(unittest.TestCase):
    def test_required_files_and_frontmatter(self):
        agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("today --json", agents_text)
        self.assertIn("6,000", readme_text)

        for skill_name in ("toefl-vocab", "toefl-speaking", "toefl-writing"):
            skill_path = ROOT / ".agents" / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill_path.exists(), f"Missing {skill_path}")
            text = skill_path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\nname: " + skill_name))
            self.assertIn("my_weakness_log.json", text)
            self.assertIn("toefl-agent-studio", text)

        vocab_text = (ROOT / ".agents" / "skills" / "toefl-vocab" / "SKILL.md").read_text(encoding="utf-8")
        for required_token in ("today --json", "record-vocab", "core", "band5", "band6", "20"):
            self.assertIn(required_token, vocab_text)

    def test_toefl_vocab_three_phase_and_feedback_contracts(self):
        vocab_text = (ROOT / ".agents" / "skills" / "toefl-vocab" / "SKILL.md").read_text(encoding="utf-8")
        for token in (
            "HARD-GATE",
            "Phase 1",
            "Phase 2",
            "Phase 3",
            "예문 1",
            "예문 2",
            "meaning_ko",
            "expression_upgrades",
            "vocab_collocation",
            "4–5 mini-groups",
            "2–3 original academic sentences",
        ):
            self.assertIn(token, vocab_text)


if __name__ == "__main__":
    unittest.main()
