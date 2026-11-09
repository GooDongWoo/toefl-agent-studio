import json
import tempfile
import unittest
from pathlib import Path
from scripts.drill import (
    mask_word_in_sentence,
    count_response_words,
    record_missed_vocab,
    create_session_file,
)


class TestDrillCLI(unittest.TestCase):
    def test_mask_word_in_sentence_short_and_long(self):
        s1 = "The results were ambiguous and hard to read."
        self.assertEqual(
            mask_word_in_sentence(s1, "ambiguous"),
            "The results were amb______ and hard to read.",
        )
        s2 = "The author seems to imply that the theory is flawed."
        self.assertEqual(
            mask_word_in_sentence(s2, "imply"),
            "The author seems to im___ that the theory is flawed.",
        )

    def test_count_response_words(self):
        sample_md = (
            "# Session\n\n"
            "## 📋 Prompt\nWrite an email.\n\n"
            "## ✍️ My Response\n"
            "Dear Professor Smith, I am writing to request an extension on my paper.\n\n"
            "## 📊 AI Evaluation\nPending.\n"
        )
        self.assertEqual(count_response_words(sample_md), 13)

    def test_record_missed_vocab_creates_and_increments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "my_weakness_log.json"
            data1 = record_missed_vocab(log_path, "assuage", "완화하다", "2026-11-09")
            self.assertEqual(data1["missed_vocab"][0]["error_count"], 1)
            data2 = record_missed_vocab(log_path, "assuage", "완화하다", "2026-11-09")
            self.assertEqual(data2["missed_vocab"][0]["error_count"], 2)

    def test_create_session_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            session_dir = Path(tmpdir)
            prompt = {
                "id": "email_01",
                "title": "Missed Quiz",
                "scenario": "You missed class.",
                "recipient": "Prof. Lee",
                "subject": "Absence",
                "bullet_points": ["Explain why", "Ask for makeup", "Ask for notes"],
            }
            out_path = create_session_file(session_dir, "email", prompt, "2026-11-09 14:00:00")
            self.assertTrue(out_path.exists())
            content = out_path.read_text(encoding="utf-8")
            self.assertIn("## ✍️ My Response", content)
            self.assertIn("Prof. Lee", content)


if __name__ == "__main__":
    unittest.main()
