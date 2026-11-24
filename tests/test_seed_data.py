import json
import re
import unittest
from collections import Counter
from pathlib import Path

from scripts.drill import mask_word_in_sentence

ROOT = Path(__file__).resolve().parent.parent
VOCAB_PATH = ROOT / "data" / "vocab_seed.json"
PROMPT_PATH = ROOT / "data" / "prompt_bank.json"

ORIGINAL_24_WORDS = {
    "ambiguous", "anomalous", "arbitrary", "assuage", "comprehensive", "constitute",
    "correlation", "differentiate", "discrepancy", "eradicate", "exemplify", "fluctuate",
    "imply", "inevitable", "mitigate", "peculiar", "pivotal", "pragmatic",
    "profound", "scarcity", "substantiate", "ubiquitous", "unprecedented", "viable",
}

ROTATION_TARGETS = {
    1: {"core": 7, "band5": 7, "band6": 6},
    2: {"core": 7, "band5": 6, "band6": 7},
    0: {"core": 6, "band5": 7, "band6": 7},
}


class TestSeedData(unittest.TestCase):
    def test_vocab_seed_schema_and_examples(self):
        self.assertTrue(VOCAB_PATH.exists(), "vocab_seed.json must exist")
        vocab = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
        total = len(vocab)
        self.assertGreaterEqual(total, 6000, "Must contain at least 6,000 TOEFL/academic words")
        self.assertEqual(total % 60, 0, "Total word count must be a multiple of 60 for 3-day tier rotation")

        required_keys = {"id", "day", "section", "word", "pos", "meaning_ko", "synonyms", "example", "collocations"}
        valid_sections = {"core", "band5", "band6"}
        seen_words = set()
        seen_ids = set()
        by_day = {}
        section_counts = Counter()

        for item in vocab:
            self.assertTrue(required_keys.issubset(item.keys()), f"Missing keys in {item}")
            word = item["word"].strip()
            w_lower = word.lower()
            self.assertTrue(word, f"Empty word in {item}")
            self.assertNotIn(w_lower, seen_words, f"Duplicate word: {word}")
            seen_words.add(w_lower)

            self.assertNotIn(item["id"], seen_ids, f"Duplicate id: {item['id']}")
            seen_ids.add(item["id"])

            self.assertIn(item["section"], valid_sections, f"Invalid section in {item}")
            section_counts[item["section"]] += 1

            self.assertTrue(item["meaning_ko"].strip(), f"Empty meaning_ko for {word}")
            self.assertGreaterEqual(len(item["synonyms"]), 2, f"Need >=2 synonyms for {word}")
            self.assertNotIn(w_lower, [s.strip().lower() for s in item["synonyms"]], f"Synonym repeats word {word}")
            self.assertGreaterEqual(len(item["collocations"]), 2, f"Need >=2 collocations for {word}")

            # Ensure exact word-boundary match so Complete the Words masking works
            self.assertRegex(
                item["example"],
                re.compile(rf"\b{re.escape(word)}\b", flags=re.IGNORECASE),
                f"Exact word '{word}' must appear as whole word in example: {item['example']}",
            )
            self.assertNotEqual(
                mask_word_in_sentence(item["example"], word),
                item["example"],
                f"CTEST masking failed for {word}",
            )

            day = item["day"]
            self.assertIsInstance(day, int)
            by_day.setdefault(day, []).append(item)

        expected_days = total // 20
        self.assertEqual(set(by_day.keys()), set(range(1, expected_days + 1)))
        for day, entries in by_day.items():
            self.assertEqual(len(entries), 20, f"Day {day} must have exactly 20 entries")
            day_sec = Counter(e["section"] for e in entries)
            self.assertEqual(dict(day_sec), ROTATION_TARGETS[day % 3], f"Day {day} rotation mismatch: {day_sec}")

        for sec in valid_sections:
            self.assertEqual(section_counts[sec], total // 3, f"Section {sec} must hold 1/3 of total")

        self.assertTrue(ORIGINAL_24_WORDS.issubset(seen_words), "All 24 original seed words must be preserved")

    def test_prompt_bank_schema(self):
        self.assertTrue(PROMPT_PATH.exists(), "prompt_bank.json must exist")
        prompts = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
        for section in ("write_an_email", "academic_discussion", "build_a_sentence", "take_an_interview"):
            self.assertIn(section, prompts)
            self.assertGreaterEqual(len(prompts[section]), 3, f"{section} must have at least 3 prompts")
        for interview in prompts["take_an_interview"]:
            self.assertEqual(len(interview["questions"]), 4, "Take an Interview must have 4 sequential questions")


if __name__ == "__main__":
    unittest.main()
