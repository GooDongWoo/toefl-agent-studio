import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import scripts.drill as drill_mod
from scripts.drill import (
    mask_word_in_sentence,
    count_response_words,
    record_missed_vocab,
    create_session_file,
    load_weakness_log,
    record_correct_vocab,
    mark_day_completed,
    select_daily_vocab,
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

    def _sample_vocab_bank(self):
        items = []
        sections = ["core", "band5", "band6"]
        for day in range(1, 4):
            for idx in range(20):
                sec = sections[idx % 3]
                word = f"wordd{day}i{idx:02d}"
                items.append(
                    {
                        "id": f"day{day:03d}_{idx+1:03d}",
                        "day": day,
                        "section": sec,
                        "word": word,
                        "pos": "noun",
                        "meaning_ko": f"뜻_{word}",
                        "synonyms": ["synA", "synB"],
                        "example": f"Academic research uses {word} in experiments.",
                        "collocations": [f"use {word}", f"{word} analysis"],
                    }
                )
        return items

    def test_select_daily_vocab_mixed_day_and_capped_review(self):
        vocab = self._sample_vocab_bank()
        log_data = {
            "missed_vocab": [
                # Day 1 word overlaps with fresh Day 1 -> must be excluded from Day 1 review
                {"word": "wordd1i00", "meaning_ko": "뜻", "section": "core", "error_count": 9, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
                # Graduated word -> excluded
                {"word": "wordd3i01", "meaning_ko": "뜻", "section": "band5", "error_count": 8, "last_missed": "2026-11-19", "streak": 2, "mastered": True},
                # 6 active non-overlapping review words -> capped at max_review=5 sorted by error_count desc
                {"word": "wordd2i00", "meaning_ko": "뜻", "section": "core", "error_count": 1, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
                {"word": "wordd2i01", "meaning_ko": "뜻", "section": "band5", "error_count": 6, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
                {"word": "wordd2i02", "meaning_ko": "뜻", "section": "band6", "error_count": 5, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
                {"word": "wordd2i03", "meaning_ko": "뜻", "section": "core", "error_count": 4, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
                {"word": "wordd2i04", "meaning_ko": "뜻", "section": "band5", "error_count": 3, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
                {"word": "wordd2i05", "meaning_ko": "뜻", "section": "band6", "error_count": 2, "last_missed": "2026-11-19", "streak": 0, "mastered": False},
            ],
            "expression_upgrades": [],
            "vocab_progress": {"current_day": 1, "completed_days": [], "last_studied": None},
        }
        bundle = select_daily_vocab(vocab, log_data, count=20, max_review=5)
        self.assertEqual(bundle["day"], 1)
        self.assertEqual(bundle["max_day"], 3)
        self.assertEqual(len(bundle["fresh_items"]), 20)
        # Fresh items ordered core -> band5 -> band6
        fresh_sections = [x["section"] for x in bundle["fresh_items"]]
        self.assertEqual(fresh_sections, sorted(fresh_sections, key=["core", "band5", "band6"].index))
        self.assertEqual(len(bundle["review_items"]), 5)
        self.assertEqual([x["word"] for x in bundle["review_items"]], ["wordd2i01", "wordd2i02", "wordd2i03", "wordd2i04", "wordd2i05"])
        self.assertIn("___", bundle["fresh_items"][0]["masked_example"])

    def test_select_daily_vocab_section_filter_respects_current_day(self):
        vocab = self._sample_vocab_bank()
        log_data = {
            "missed_vocab": [],
            "expression_upgrades": [],
            "vocab_progress": {"current_day": 2, "completed_days": [1], "last_studied": "2026-11-19"},
        }
        bundle = select_daily_vocab(vocab, log_data, section="band6", count=10, include_review=False)
        self.assertEqual(len(bundle["fresh_items"]), 10)
        self.assertTrue(all(x["section"] == "band6" for x in bundle["fresh_items"]))
        self.assertTrue(all(x["day"] >= 2 for x in bundle["fresh_items"]))

    def test_cli_today_json_and_record_vocab_and_stats(self):
        vocab = self._sample_vocab_bank()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            seed_path = tmp / "vocab_seed.json"
            log_path = tmp / "my_weakness_log.json"
            sessions_dir = tmp / "sessions"
            sessions_dir.mkdir()
            seed_path.write_text(json.dumps(vocab), encoding="utf-8")

            with (
                mock.patch.object(drill_mod, "VOCAB_SEED_PATH", seed_path),
                mock.patch.object(drill_mod, "WEAKNESS_LOG_PATH", log_path),
                mock.patch.object(drill_mod, "SESSIONS_DIR", sessions_dir),
            ):
                parser = drill_mod.build_parser()

                # 1. today --json
                buf = io.StringIO()
                with redirect_stdout(buf):
                    args = parser.parse_args(["today", "--json"])
                    drill_mod.cmd_today(args)
                payload = json.loads(buf.getvalue())
                self.assertEqual(payload["day"], 1)
                self.assertEqual(len(payload["fresh_items"]), 20)
                self.assertEqual(payload["counts"]["fresh"], 20)

                # 2. record-vocab missed + complete-day 1
                args_rec = parser.parse_args(
                    ["record-vocab", "--missed", "wordd1i00", "--complete-day", "1"]
                )
                with redirect_stdout(io.StringIO()):
                    drill_mod.cmd_record_vocab(args_rec)

                saved = load_weakness_log(log_path)
                self.assertEqual(saved["vocab_progress"]["current_day"], 2)
                self.assertEqual(saved["vocab_progress"]["completed_days"], [1])
                self.assertEqual(saved["missed_vocab"][0]["word"], "wordd1i00")
                self.assertEqual(saved["missed_vocab"][0]["section"], "core")
                self.assertEqual(saved["missed_vocab"][0]["meaning_ko"], "뜻_wordd1i00")

                # 3. passed twice graduates the word
                for _ in range(2):
                    args_pass = parser.parse_args(["record-vocab", "--passed", "wordd1i00"])
                    with redirect_stdout(io.StringIO()):
                        drill_mod.cmd_record_vocab(args_pass)
                saved2 = load_weakness_log(log_path)
                self.assertTrue(saved2["missed_vocab"][0]["mastered"])

                # 4. stats renders progress
                stats_buf = io.StringIO()
                with redirect_stdout(stats_buf):
                    drill_mod.cmd_stats(parser.parse_args(["stats"]))
                stats_out = stats_buf.getvalue()
                self.assertIn("Day 2 / 3", stats_out)
                self.assertIn("Graduated (Mastered): 1", stats_out)

    def test_cli_ctest_modes_and_interactive(self):
        vocab = self._sample_vocab_bank()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            seed_path = tmp / "vocab_seed.json"
            log_path = tmp / "my_weakness_log.json"
            seed_path.write_text(json.dumps(vocab), encoding="utf-8")

            with (
                mock.patch.object(drill_mod, "VOCAB_SEED_PATH", seed_path),
                mock.patch.object(drill_mod, "WEAKNESS_LOG_PATH", log_path),
            ):
                parser = drill_mod.build_parser()

                # Default --count 20 with --json
                buf = io.StringIO()
                with redirect_stdout(buf):
                    args = parser.parse_args(["ctest", "--json"])
                    drill_mod.cmd_ctest(args)
                payload = json.loads(buf.getvalue())
                self.assertEqual(payload["mode"], "Day 1")
                self.assertEqual(len(payload["items"]), 20)

                # --section and --no-review
                buf_sec = io.StringIO()
                with redirect_stdout(buf_sec):
                    args_sec = parser.parse_args(["ctest", "--section", "band5", "--count", "3", "--no-review", "--json"])
                    drill_mod.cmd_ctest(args_sec)
                payload_sec = json.loads(buf_sec.getvalue())
                self.assertEqual(len(payload_sec["items"]), 3)
                self.assertTrue(all(x["section"] == "band5" for x in payload_sec["items"]))

                # --interactive marks day completed and logs missed word
                answers = iter(["wrong"] + [x["word"] for x in payload["items"][1:]])
                with (
                    mock.patch("builtins.input", side_effect=lambda _: next(answers)),
                    redirect_stdout(io.StringIO()),
                ):
                    drill_mod.cmd_ctest(parser.parse_args(["ctest", "--interactive"]))
                saved = load_weakness_log(log_path)
                self.assertEqual(saved["vocab_progress"]["completed_days"], [1])
                self.assertEqual(saved["vocab_progress"]["current_day"], 2)
                self.assertEqual(len(saved["missed_vocab"]), 1)

                # --review --json surfaces only active review word
                buf_rev = io.StringIO()
                with redirect_stdout(buf_rev):
                    drill_mod.cmd_ctest(parser.parse_args(["ctest", "--review", "--json"]))
                payload_rev = json.loads(buf_rev.getvalue())
                self.assertEqual(payload_rev["mode"], "Active Review Only")
                self.assertEqual(len(payload_rev["items"]), 1)
                self.assertTrue(payload_rev["items"][0]["is_review"])


if __name__ == "__main__":
    unittest.main()
