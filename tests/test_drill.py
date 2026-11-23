import json
import tempfile
import unittest
from pathlib import Path
from scripts.drill import (
    mask_word_in_sentence,
    count_response_words,
    record_missed_vocab,
    create_session_file,
    load_weakness_log,
    record_correct_vocab,
    mark_day_completed,
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

    def test_load_weakness_log_backward_compatible_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "my_weakness_log.json"
            legacy = {
                "missed_vocab": [
                    {
                        "word": "assuage",
                        "meaning_ko": "완화하다",
                        "error_count": 2,
                        "last_missed": "2026-11-09",
                    }
                ],
                "expression_upgrades": [],
            }
            log_path.write_text(json.dumps(legacy), encoding="utf-8")
            loaded = load_weakness_log(log_path)
            self.assertEqual(loaded["vocab_progress"]["current_day"], 1)
            self.assertEqual(loaded["vocab_progress"]["completed_days"], [])
            self.assertIsNone(loaded["vocab_progress"]["last_studied"])
            self.assertEqual(loaded["missed_vocab"][0]["streak"], 0)
            self.assertFalse(loaded["missed_vocab"][0]["mastered"])
            self.assertEqual(loaded["missed_vocab"][0]["section"], "")

    def test_record_correct_vocab_graduates_at_two_and_missed_resets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "my_weakness_log.json"
            record_missed_vocab(log_path, "assuage", "완화하다", "2026-11-20", section="band6")

            d1 = record_correct_vocab(log_path, "assuage")
            self.assertEqual(d1["missed_vocab"][0]["streak"], 1)
            self.assertFalse(d1["missed_vocab"][0]["mastered"])

            d2 = record_correct_vocab(log_path, "assuage")
            self.assertEqual(d2["missed_vocab"][0]["streak"], 2)
            self.assertTrue(d2["missed_vocab"][0]["mastered"])

            # Missing a graduated word re-activates it and resets streak
            d3 = record_missed_vocab(log_path, "assuage", "완화하다", "2026-11-21", section="band6")
            self.assertEqual(d3["missed_vocab"][0]["error_count"], 2)
            self.assertEqual(d3["missed_vocab"][0]["streak"], 0)
            self.assertFalse(d3["missed_vocab"][0]["mastered"])
            self.assertEqual(d3["missed_vocab"][0]["section"], "band6")

    def test_mark_day_completed_advances_current_day(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "my_weakness_log.json"
            d1 = mark_day_completed(log_path, day=1, max_day=300, today_iso="2026-11-20")
            self.assertEqual(d1["vocab_progress"]["completed_days"], [1])
            self.assertEqual(d1["vocab_progress"]["current_day"], 2)
            self.assertEqual(d1["vocab_progress"]["last_studied"], "2026-11-20")

            # Completing day 3 while day 2 is uncompleted keeps current_day at 2
            d2 = mark_day_completed(log_path, day=3, max_day=300, today_iso="2026-11-20")
            self.assertEqual(d2["vocab_progress"]["completed_days"], [1, 3])
            self.assertEqual(d2["vocab_progress"]["current_day"], 2)

            # Completing day 2 advances current_day past 3 to 4
            d3 = mark_day_completed(log_path, day=2, max_day=300, today_iso="2026-11-21")
            self.assertEqual(d3["vocab_progress"]["completed_days"], [1, 2, 3])
            self.assertEqual(d3["vocab_progress"]["current_day"], 4)


if __name__ == "__main__":
    unittest.main()
