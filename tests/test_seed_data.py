import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOCAB_PATH = ROOT / "data" / "vocab_seed.json"
PROMPT_PATH = ROOT / "data" / "prompt_bank.json"


class TestSeedData(unittest.TestCase):
    def test_vocab_seed_schema_and_examples(self):
        self.assertTrue(VOCAB_PATH.exists(), "vocab_seed.json must exist")
        vocab = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(vocab), 20, "Must contain at least 20 high-frequency words")
        required_keys = {"id", "day", "word", "pos", "meaning_ko", "synonyms", "example", "collocations"}
        for item in vocab:
            self.assertTrue(required_keys.issubset(item.keys()), f"Missing keys in {item}")
            self.assertIn(item["word"].lower(), item["example"].lower(), f"Word {item['word']} must appear in example")
            self.assertGreaterEqual(len(item["synonyms"]), 2)

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
