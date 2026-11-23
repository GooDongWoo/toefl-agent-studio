# TOEFL Agent Studio 6,000+ Vocab Expansion & Daily 20-Word Section Learning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand `toefl-agent-studio` from 24 words to a 6,000-word (300-day × 20-word/day) 3-tier (`core`, `band5`, `band6`) vocabulary bank with stateful progress/graduation tracking, a section-based 3-round `$toefl-vocab` workflow, global `~/.agents/skills` junctions, and synced Obsidian specs.

**Architecture:** Keep `data/vocab_seed.json` as a single backward-compatible JSON database containing 6,000 curated words in an even 3-day `7/7/6` tier rotation (`2,000` each across `core`, `band5`, `band6`), while preventing LLM context bloat by routing all agent lookups through `python scripts/drill.py today --json`. Extend `data/my_weakness_log.json` backward-compatibly with `vocab_progress` and review `streak`/`mastered` graduation (graduating after 2 consecutive correct recalls), expose deterministic CLI commands (`today`, `record-vocab`, updated `ctest`/`stats`), and link all 3 TOEFL skills globally via `sync-agent-links.ps1` with CWD-first + `~/toefl-agent-studio` fallback resolution.

**Tech Stack:** Python 3.10+ Standard Library (`argparse`, `json`, `pathlib`, `re`, `datetime`, `unittest`, `urllib.request` at build-time only), Markdown (`SKILL.md`, `AGENTS.md`, `README.md`), PowerShell (`sync-agent-links.ps1`), Antigravity `run_workflow` (for parallel 6,000-word enrichment).

**Spec:** [docs/superpowers/specs/2026-11-20-vocab-expansion-design.md](../specs/2026-11-20-vocab-expansion-design.md)

## Global Constraints

- Runtime code in `scripts/drill.py` and `tests/` MUST use only the Python 3.10+ standard library (zero external dependencies; `git clone` / `git pull` on corporate work PC must work immediately).
- All file I/O MUST explicitly use `encoding="utf-8"`.
- `data/vocab_seed.json` total entries MUST be `>= 6000` and divisible by `60` (initial build target: exactly `6,000` = `300` days × `20` words/day, `2,000` per tier `core` / `band5` / `band6`).
- Every Day `1..N` MUST have exactly `20` words following the 3-day rotation (`day % 3 == 1`: 7/7/6, `day % 3 == 2`: 7/6/7, `day % 3 == 0`: 6/7/7 across `core`/`band5`/`band6`).
- All 24 original seed words (`ambiguous` through `viable`) MUST be preserved in Day 1–2 without duplication.
- Every `vocab_seed.json` entry MUST match `re.search(rf"\b{re.escape(word)}\b", example, re.IGNORECASE)` so `mask_word_in_sentence` always masks the target word.
- `data/my_weakness_log.json` MUST remain backward-compatible with older files missing `vocab_progress`, `streak`, `mastered`, or `section`.
- `.agents/skills/toefl-vocab/SKILL.md` MUST forbid direct `read_file` on `data/vocab_seed.json` and require `python scripts/drill.py today --json`.
- All 3 TOEFL skills MUST resolve relative paths (`./`) when inside the repo, falling back to `~/toefl-agent-studio` when invoked globally from outside the repo.

---

## File Structure

| File | Responsibility | Action |
| :--- | :--- | :--- |
| `C:\Users\dongwoo\toefl-agent-studio\scripts\drill.py` | Weakness log loader/saver, review streak/graduation, day progress, daily/section vocab selector, `today` & `record-vocab` subcommands, updated `ctest` (default 20) & `stats` | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\tests\test_drill.py` | Unit and CLI tests for state migration, `record_correct_vocab`, `record_missed_vocab` reset, `mark_day_completed`, `select_daily_vocab`, `today --json`, `record-vocab`, `ctest`, `stats` | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\tests\test_seed_data.py` | Validation suite for `>= 6000` words, multiple of 60, `7/7/6` rotation, `section`, uniqueness, 24-word preservation, `\bword\b` CTEST regex | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\data\vocab_seed.json` | Curated 6,000-word academic/TOEFL dataset across `core`, `band5`, `band6` (`day` 1–300) | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-vocab\SKILL.md` | 3-round section mini-batch workflow, `today --json` guardrail, `record-vocab` wrap-up, repo fallback | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-speaking\SKILL.md` | Add CWD-first + `~/toefl-agent-studio` fallback rule | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-writing\SKILL.md` | Add CWD-first + `~/toefl-agent-studio` fallback rule | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\tests\test_skills_integrity.py` | Assert frontmatter, 20-word + 3-section + `today --json` guardrail in `toefl-vocab`, fallback & `my_weakness_log.json` in all 3 skills | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\AGENTS.md` | Update `$toefl-vocab` summary & CLI integration reference (`today`, `record-vocab`, `ctest`, `stats`) | Modify |
| `C:\Users\dongwoo\toefl-agent-studio\README.md` | Update repo overview, 6,000-word / 300-day / 3-section guide, and CLI examples | Modify |
| `C:\Users\dongwoo\.agents\.gitignore` | Ignore local project skill junctions `skills/toefl-vocab`, `skills/toefl-speaking`, `skills/toefl-writing` | Modify |
| `C:\Users\dongwoo\.agents\scripts\sync-agent-links.ps1` | Create junctions for all 3 TOEFL skills from `~/toefl-agent-studio/.agents/skills/` to `~/.agents/skills/` and agent runtimes | Modify |
| `C:\Users\dongwoo\OneDrive - 경희대학교\Obsidian\20_Projects\[어학] 토익_오픽_토플\03_토플\03_사내PC_토플_에이전트_스튜디오_스펙.md` | Update schema/CLI/skill spec to 6,000+ words & check off home-PC 20+/day sync item | Modify |
| `C:\Users\dongwoo\OneDrive - 경희대학교\Obsidian\20_Projects\[어학] 토익_오픽_토플\03_토플\00_토플_마스터_대시보드.md` | Log completion of 6,000+ vocab & 20+/day section expansion | Modify |

*(Build-time temporary scripts and batch intermediate files for Task 3 are kept in the conversation scratch directory `C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch\` so `toefl-agent-studio` stays clean.)*

---

### Task 1: Weakness Log State Helpers & Review Graduation Logic

**Files:**
- Modify: `C:\Users\dongwoo\toefl-agent-studio\scripts\drill.py:79-130`
- Test: `C:\Users\dongwoo\toefl-agent-studio\tests\test_drill.py:1-63`

**Interfaces:**
- Consumes: `WEAKNESS_LOG_PATH` (`Path`), standard library `json`, `pathlib.Path`.
- Produces (exported from `scripts.drill`):
  - `load_weakness_log(log_path: Path) -> Dict[str, Any]`
  - `save_weakness_log(log_path: Path, data: Dict[str, Any]) -> None`
  - `record_missed_vocab(log_path: Path, word: str, meaning_ko: str, today_iso: str, section: str = "") -> Dict[str, Any]`
  - `record_correct_vocab(log_path: Path, word: str) -> Dict[str, Any]`
  - `mark_day_completed(log_path: Path, day: int, max_day: int, today_iso: str) -> Dict[str, Any]`

- [ ] **Step 1: Write the failing unit tests in `tests/test_drill.py`**

Append imports and tests to `C:\Users\dongwoo\toefl-agent-studio\tests\test_drill.py`:

```python
from scripts.drill import (
    mask_word_in_sentence,
    count_response_words,
    record_missed_vocab,
    create_session_file,
    load_weakness_log,
    record_correct_vocab,
    mark_day_completed,
)
```

Add test methods inside `TestDrillCLI`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest tests.test_drill -v`
Expected: FAIL with `ImportError: cannot import name 'load_weakness_log' from 'scripts.drill'`.

- [ ] **Step 3: Implement state helpers in `scripts/drill.py`**

Replace lines 79–130 in `C:\Users\dongwoo\toefl-agent-studio\scripts\drill.py` with:

```python
DEFAULT_VOCAB_PROGRESS: Dict[str, Any] = {
    "current_day": 1,
    "completed_days": [],
    "last_studied": None,
}


def load_weakness_log(log_path: Path) -> Dict[str, Any]:
    """Load weakness log JSON safely with backward-compatible defaults."""
    log_path = Path(log_path)
    data: Dict[str, Any] = {
        "missed_vocab": [],
        "expression_upgrades": [],
        "vocab_progress": dict(DEFAULT_VOCAB_PROGRESS),
    }
    if log_path.exists():
        try:
            loaded = json.loads(log_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            pass

    if not isinstance(data.get("missed_vocab"), list):
        data["missed_vocab"] = []
    if not isinstance(data.get("expression_upgrades"), list):
        data["expression_upgrades"] = []

    normalized_missed: List[Dict[str, Any]] = []
    for item in data["missed_vocab"]:
        if not isinstance(item, dict) or not item.get("word"):
            continue
        item.setdefault("meaning_ko", "")
        item.setdefault("section", "")
        item.setdefault("error_count", 1)
        item.setdefault("last_missed", "")
        item.setdefault("streak", 0)
        item.setdefault("mastered", False)
        normalized_missed.append(item)
    data["missed_vocab"] = normalized_missed

    progress = data.get("vocab_progress")
    if not isinstance(progress, dict):
        progress = {}
    completed = progress.get("completed_days")
    if not isinstance(completed, list):
        completed = []
    clean_completed = sorted({int(d) for d in completed if isinstance(d, int) and d >= 1})
    current_day = progress.get("current_day", 1)
    if not isinstance(current_day, int) or current_day < 1:
        current_day = 1
    data["vocab_progress"] = {
        "current_day": current_day,
        "completed_days": clean_completed,
        "last_studied": progress.get("last_studied"),
    }
    return data


def save_weakness_log(log_path: Path, data: Dict[str, Any]) -> None:
    """Persist weakness log JSON cleanly in UTF-8."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def record_missed_vocab(
    log_path: Path,
    word: str,
    meaning_ko: str,
    today_iso: str,
    section: str = "",
) -> Dict[str, Any]:
    """Record a missed vocabulary word into the weakness JSON log.

    If word exists (case-insensitive), increments error_count, resets streak/mastered,
    and updates last_missed. Otherwise appends a new entry.
    """
    data = load_weakness_log(log_path)
    target_word = word.strip().lower()
    found = False
    for item in data["missed_vocab"]:
        if item.get("word", "").strip().lower() == target_word:
            item["error_count"] = item.get("error_count", 0) + 1
            item["last_missed"] = today_iso
            item["streak"] = 0
            item["mastered"] = False
            if meaning_ko and not item.get("meaning_ko"):
                item["meaning_ko"] = meaning_ko.strip()
            if section and not item.get("section"):
                item["section"] = section.strip()
            found = True
            break

    if not found:
        data["missed_vocab"].append(
            {
                "word": word.strip(),
                "meaning_ko": meaning_ko.strip(),
                "section": section.strip(),
                "error_count": 1,
                "last_missed": today_iso,
                "streak": 0,
                "mastered": False,
            }
        )

    save_weakness_log(log_path, data)
    return data


def record_correct_vocab(log_path: Path, word: str) -> Dict[str, Any]:
    """Increment recall streak for an active missed word and graduate at streak >= 2."""
    data = load_weakness_log(log_path)
    target_word = word.strip().lower()
    changed = False
    for item in data["missed_vocab"]:
        if item.get("word", "").strip().lower() == target_word and not item.get("mastered", False):
            new_streak = int(item.get("streak", 0)) + 1
            item["streak"] = new_streak
            if new_streak >= 2:
                item["mastered"] = True
            changed = True
            break

    if changed or not Path(log_path).exists():
        save_weakness_log(log_path, data)
    return data


def mark_day_completed(
    log_path: Path, day: int, max_day: int, today_iso: str
) -> Dict[str, Any]:
    """Record day completion and advance current_day to the lowest uncompleted day."""
    data = load_weakness_log(log_path)
    progress = data["vocab_progress"]
    completed = set(progress.get("completed_days", []))
    if day >= 1:
        completed.add(day)
    progress["completed_days"] = sorted(completed)
    progress["last_studied"] = today_iso

    safe_max = max(1, max_day)
    next_day = safe_max
    for candidate in range(1, safe_max + 1):
        if candidate not in completed:
            next_day = candidate
            break
    progress["current_day"] = next_day

    save_weakness_log(log_path, data)
    return data
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest discover -s tests -p "test_*.py" -v`
Expected: PASS (10 tests OK).

- [ ] **Step 5: Commit Task 1**

```bash
git -C C:\Users\dongwoo\toefl-agent-studio add scripts/drill.py tests/test_drill.py
git -C C:\Users\dongwoo\toefl-agent-studio commit -m "feat(cli): add weakness log migration, review graduation, and day progress helpers"
```

---

### Task 2: Daily & Section Selection Logic and CLI Subcommands (`today`, `record-vocab`, `ctest`, `stats`)

**Files:**
- Modify: `C:\Users\dongwoo\toefl-agent-studio\scripts\drill.py:249-530`
- Test: `C:\Users\dongwoo\toefl-agent-studio\tests\test_drill.py`

**Interfaces:**
- Consumes: `load_weakness_log`, `record_missed_vocab`, `record_correct_vocab`, `mark_day_completed`, `mask_word_in_sentence` from Task 1.
- Produces (exported from `scripts.drill`):
  - `VALID_SECTIONS = ("core", "band5", "band6")`
  - `select_daily_vocab(vocab_items: List[Dict[str, Any]], log_data: Dict[str, Any], day: Optional[int] = None, section: Optional[str] = None, count: int = 20, max_review: int = 5, include_review: bool = True) -> Dict[str, Any]`
  - CLI subcommands:
    - `python scripts/drill.py today [--day N] [--section {core,band5,band6}] [--count 20] [--max-review 5] [--no-review] [--json] [--complete]`
    - `python scripts/drill.py record-vocab [--missed WORD ...] [--passed WORD ...] [--complete-day N]`
    - `python scripts/drill.py ctest [--day N] [--section {core,band5,band6}] [--count 20] [--review | --no-review] [--interactive] [--json]`
    - `python scripts/drill.py stats`

- [ ] **Step 1: Write failing tests for `select_daily_vocab` and the new/updated CLI commands in `tests/test_drill.py`**

Update imports in `C:\Users\dongwoo\toefl-agent-studio\tests\test_drill.py` to include `subprocess`, `sys`, and `select_daily_vocab`, `cmd_today`, `cmd_record_vocab`, `cmd_stats`, `build_parser`, plus `scripts.drill` module reference for patching paths in unit tests:

```python
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
```

Add test methods inside `TestDrillCLI`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest tests.test_drill -v`
Expected: FAIL with `ImportError: cannot import name 'select_daily_vocab' from 'scripts.drill'`.

- [ ] **Step 3: Implement `select_daily_vocab`, `cmd_today`, `cmd_record_vocab`, updated `cmd_ctest`, `cmd_stats`, and `build_parser` in `scripts/drill.py`**

Add `VALID_SECTIONS = ("core", "band5", "band6")` near the top constants in `C:\Users\dongwoo\toefl-agent-studio\scripts\drill.py`, and replace lines 249–530 (from `_load_json_file` to `main`) with:

```python
VALID_SECTIONS = ("core", "band5", "band6")


def _load_json_file(file_path: Path) -> Any:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return json.loads(file_path.read_text(encoding="utf-8"))


def _section_sort_key(item: Dict[str, Any]) -> tuple[int, str]:
    sec = item.get("section", "")
    rank = VALID_SECTIONS.index(sec) if sec in VALID_SECTIONS else len(VALID_SECTIONS)
    return (rank, item.get("id", item.get("word", "")))


def _enrich_item_for_drill(item: Dict[str, Any], is_review: bool = False) -> Dict[str, Any]:
    word = item.get("word", "")
    example = item.get("example", "")
    enriched = {
        "id": item.get("id", ""),
        "day": item.get("day"),
        "section": item.get("section", ""),
        "word": word,
        "pos": item.get("pos", ""),
        "meaning_ko": item.get("meaning_ko", ""),
        "synonyms": item.get("synonyms", []),
        "example": example,
        "masked_example": mask_word_in_sentence(example, word) if example else "",
        "collocations": item.get("collocations", []),
        "is_review": is_review,
    }
    if is_review:
        enriched["error_count"] = item.get("error_count", 1)
        enriched["streak"] = item.get("streak", 0)
    return enriched


def select_daily_vocab(
    vocab_items: List[Dict[str, Any]],
    log_data: Dict[str, Any],
    day: Optional[int] = None,
    section: Optional[str] = None,
    count: int = 20,
    max_review: int = 5,
    include_review: bool = True,
) -> Dict[str, Any]:
    """Select today's fresh words (ordered by tier) and capped active review words."""
    max_day = max((int(v.get("day", 1)) for v in vocab_items if isinstance(v.get("day"), int)), default=1)
    current_day = int(log_data.get("vocab_progress", {}).get("current_day", 1) or 1)
    target_day = day if day is not None else min(current_day, max_day)

    seed_by_word = {v["word"].strip().lower(): v for v in vocab_items if v.get("word")}

    if section is not None:
        if day is not None:
            candidates = [
                v for v in vocab_items
                if v.get("day") == target_day and v.get("section") == section
            ]
        else:
            candidates = [
                v for v in vocab_items
                if v.get("section") == section and int(v.get("day", 1)) >= target_day
            ]
            if len(candidates) < count:
                earlier = [
                    v for v in vocab_items
                    if v.get("section") == section and int(v.get("day", 1)) < target_day
                ]
                candidates.extend(earlier)
    else:
        candidates = [v for v in vocab_items if v.get("day") == target_day]
        candidates.sort(key=_section_sort_key)

    fresh_raw = candidates[: max(0, count)]
    fresh_items = [_enrich_item_for_drill(v, is_review=False) for v in fresh_raw]
    fresh_words = {v["word"].strip().lower() for v in fresh_items}

    review_items: List[Dict[str, Any]] = []
    if include_review and max_review > 0:
        active_missed = [
            m for m in log_data.get("missed_vocab", [])
            if not m.get("mastered", False)
            and m.get("word", "").strip().lower() not in fresh_words
        ]
        if section is not None:
            active_missed = [
                m for m in active_missed
                if (m.get("section") or seed_by_word.get(m["word"].strip().lower(), {}).get("section")) == section
            ]
        active_missed.sort(
            key=lambda m: (int(m.get("error_count", 0)), m.get("last_missed", "")),
            reverse=True,
        )
        for m in active_missed[:max_review]:
            w_lower = m["word"].strip().lower()
            seed_match = seed_by_word.get(w_lower)
            if seed_match:
                merged = dict(seed_match)
                merged["error_count"] = m.get("error_count", 1)
                merged["streak"] = m.get("streak", 0)
                review_items.append(_enrich_item_for_drill(merged, is_review=True))
            else:
                review_items.append(
                    _enrich_item_for_drill(
                        {
                            "word": m["word"],
                            "meaning_ko": m.get("meaning_ko", ""),
                            "section": m.get("section", ""),
                            "error_count": m.get("error_count", 1),
                            "streak": m.get("streak", 0),
                        },
                        is_review=True,
                    )
                )

    section_counts = {sec: sum(1 for x in fresh_items if x.get("section") == sec) for sec in VALID_SECTIONS}
    return {
        "day": target_day,
        "max_day": max_day,
        "section_filter": section,
        "fresh_items": fresh_items,
        "review_items": review_items,
        "counts": {
            "fresh": len(fresh_items),
            "review": len(review_items),
            "total": len(fresh_items) + len(review_items),
            "by_section": section_counts,
        },
    }


def _print_vocab_bundle(bundle: Dict[str, Any]) -> None:
    day_label = f"Day {bundle['day']} / {bundle['max_day']}"
    sec_label = bundle["section_filter"] or "All Sections (Core + Band 5.0 + Band 6.0)"
    counts = bundle["counts"]
    print(f"\n=== TOEFL Daily Vocabulary ({day_label} | {sec_label}) ===")
    print(f"Fresh: {counts['fresh']} | Review: {counts['review']} | Total: {counts['total']}\n")

    idx = 1
    for sec in VALID_SECTIONS:
        sec_items = [x for x in bundle["fresh_items"] if x.get("section") == sec]
        if not sec_items:
            continue
        print(f"--- Section: {sec.upper()} ({len(sec_items)}) ---")
        for item in sec_items:
            syns = ", ".join(item.get("synonyms", []))
            print(f"{idx}. [{item.get('pos', '')}] {item['word']} — {item.get('meaning_ko', '')}")
            print(f"   CTEST: {item['masked_example']}")
            print(f"   Synonyms: {syns}")
            idx += 1
        print()

    if bundle["review_items"]:
        print(f"--- Active Review ({len(bundle['review_items'])}) ---")
        for item in bundle["review_items"]:
            tag = (item.get("section") or "review").upper()
            print(
                f"{idx}. [REVIEW:{tag}] {item['word']} (Errors: {item.get('error_count', 1)}, "
                f"Streak: {item.get('streak', 0)}/2) — {item.get('meaning_ko', '')}"
            )
            if item.get("masked_example"):
                print(f"   CTEST: {item['masked_example']}")
            idx += 1
        print()


def cmd_today(args: argparse.Namespace) -> None:
    """Handle 'today' subcommand: output daily 20 fresh + up to 5 active review words."""
    vocab_items: List[Dict[str, Any]] = _load_json_file(VOCAB_SEED_PATH)
    log_data = load_weakness_log(WEAKNESS_LOG_PATH)

    bundle = select_daily_vocab(
        vocab_items=vocab_items,
        log_data=log_data,
        day=args.day,
        section=args.section,
        count=args.count,
        max_review=0 if args.no_review else args.max_review,
        include_review=not args.no_review,
    )

    if args.complete and bundle["fresh_items"] and args.section is None:
        today_iso = datetime.now().strftime("%Y-%m-%d")
        mark_day_completed(WEAKNESS_LOG_PATH, bundle["day"], bundle["max_day"], today_iso)

    if args.json:
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
    else:
        _print_vocab_bundle(bundle)


def cmd_record_vocab(args: argparse.Namespace) -> None:
    """Handle 'record-vocab' subcommand: atomically log missed, passed, and day completion."""
    vocab_items: List[Dict[str, Any]] = _load_json_file(VOCAB_SEED_PATH)
    seed_by_word = {v["word"].strip().lower(): v for v in vocab_items if v.get("word")}
    max_day = max((int(v.get("day", 1)) for v in vocab_items if isinstance(v.get("day"), int)), default=1)
    today_iso = datetime.now().strftime("%Y-%m-%d")

    missed_list = args.missed or []
    passed_list = args.passed or []

    for w in missed_list:
        meta = seed_by_word.get(w.strip().lower(), {})
        record_missed_vocab(
            WEAKNESS_LOG_PATH,
            w.strip(),
            meta.get("meaning_ko", ""),
            today_iso,
            section=meta.get("section", ""),
        )

    for w in passed_list:
        record_correct_vocab(WEAKNESS_LOG_PATH, w.strip())

    if args.complete_day is not None:
        mark_day_completed(WEAKNESS_LOG_PATH, args.complete_day, max_day, today_iso)

    updated = load_weakness_log(WEAKNESS_LOG_PATH)
    progress = updated["vocab_progress"]
    active_cnt = sum(1 for m in updated["missed_vocab"] if not m.get("mastered", False))
    mastered_cnt = sum(1 for m in updated["missed_vocab"] if m.get("mastered", False))
    print(
        f"Recorded vocab update: missed={len(missed_list)}, passed={len(passed_list)}, "
        f"current_day={progress['current_day']}/{max_day}, "
        f"active_missed={active_cnt}, mastered={mastered_cnt}"
    )


def cmd_ctest(args: argparse.Namespace) -> None:
    """Handle 'ctest' subcommand: Complete the Words drill."""
    vocab_items: List[Dict[str, Any]] = _load_json_file(VOCAB_SEED_PATH)
    log_data = load_weakness_log(WEAKNESS_LOG_PATH)

    if args.review:
        bundle = select_daily_vocab(
            vocab_items=vocab_items,
            log_data=log_data,
            day=args.day,
            section=args.section,
            count=0,
            max_review=args.count,
            include_review=True,
        )
        selected = [x for x in bundle["review_items"] if x.get("example")]
        mode_label = "Active Review Only"
    else:
        bundle = select_daily_vocab(
            vocab_items=vocab_items,
            log_data=log_data,
            day=args.day,
            section=args.section,
            count=args.count,
            max_review=0 if args.no_review else 5,
            include_review=not args.no_review,
        )
        selected = bundle["fresh_items"] + bundle["review_items"]
        mode_label = f"Day {bundle['day']}"

    if not selected:
        print("No matching vocabulary items found.")
        return

    if args.json:
        print(json.dumps({"mode": mode_label, "items": selected}, ensure_ascii=False, indent=2))
        return

    today_iso = datetime.now().strftime("%Y-%m-%d")

    if args.interactive:
        print("\n=======================================================")
        print(" TOEFL Complete the Words Drill (Interactive Quiz)")
        print(f" Items: {len(selected)} | Scope: {mode_label} | Section: {args.section or 'All'}")
        print("=======================================================\n")
        score = 0
        interrupted = False
        for i, item in enumerate(selected, 1):
            word = item["word"]
            masked = item.get("masked_example") or mask_word_in_sentence(item["example"], word)
            sec_badge = (item.get("section") or "general").upper()
            rev_badge = " [REVIEW]" if item.get("is_review") else ""
            print(f"[{i}/{len(selected)}] [{sec_badge}]{rev_badge} [{item.get('pos', '')}] {item.get('meaning_ko', '')}")
            print(f"Context: {masked}")
            try:
                user_ans = input("Your answer: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nQuiz interrupted.")
                interrupted = True
                break

            if user_ans.lower() == word.lower():
                print(" -> [CORRECT]\n")
                score += 1
                if item.get("is_review"):
                    record_correct_vocab(WEAKNESS_LOG_PATH, word)
            else:
                print(f" -> [INCORRECT] Correct answer: {word}\n")
                record_missed_vocab(
                    WEAKNESS_LOG_PATH,
                    word,
                    item.get("meaning_ko", ""),
                    today_iso,
                    section=item.get("section", ""),
                )

        if not interrupted and not args.review and args.section is None and bundle["fresh_items"]:
            mark_day_completed(WEAKNESS_LOG_PATH, bundle["day"], bundle["max_day"], today_iso)

        print(f"--- Drill Complete: {score}/{len(selected)} correct ---")
        if score < len(selected):
            print(f"Missed words logged to {WEAKNESS_LOG_PATH}")
    else:
        print(f"\n=== TOEFL Complete the Words Drill ({mode_label}, Count: {len(selected)}) ===\n")
        for i, item in enumerate(selected, 1):
            word = item["word"]
            masked = item.get("masked_example") or mask_word_in_sentence(item["example"], word)
            synonyms = ", ".join(item.get("synonyms", []))
            sec_badge = (item.get("section") or "general").upper()
            rev_badge = " [REVIEW]" if item.get("is_review") else ""
            print(f"{i}. [{sec_badge}]{rev_badge} [{item.get('pos', '')}] {item.get('meaning_ko', '')}")
            print(f"   Context: {masked}")
            print(f"   Answer:  {word} (Synonyms: {synonyms})")
            print()


def cmd_new_session(args: argparse.Namespace) -> None:
    """Handle 'new-session' subcommand: create worksheet markdown."""
    prompt_bank: Dict[str, List[Dict[str, Any]]] = _load_json_file(PROMPT_BANK_PATH)

    type_mapping = {
        "email": "write_an_email",
        "write_an_email": "write_an_email",
        "discussion": "academic_discussion",
        "academic_discussion": "academic_discussion",
        "interview": "take_an_interview",
        "take_an_interview": "take_an_interview",
        "sentence": "build_a_sentence",
        "build_a_sentence": "build_a_sentence",
    }

    category_key = type_mapping.get(args.type.lower())
    if not category_key or category_key not in prompt_bank:
        print(f"Unknown prompt type '{args.type}'. Choose from: email, discussion, interview, sentence.")
        sys.exit(1)

    prompts = prompt_bank[category_key]
    if not prompts:
        print(f"No prompts found in category '{category_key}'.")
        sys.exit(1)

    selected_prompt: Optional[Dict[str, Any]] = None
    if getattr(args, "id", None):
        for p in prompts:
            if p.get("id") == args.id:
                selected_prompt = p
                break
        if not selected_prompt:
            print(f"Prompt with id '{args.id}' not found in category '{category_key}'.")
            sys.exit(1)
    else:
        selected_prompt = prompts[0]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_path = create_session_file(
        session_dir=SESSIONS_DIR,
        prompt_type=args.type.lower(),
        prompt_data=selected_prompt,
        now_str=now_str,
    )

    print("Created new practice session:")
    print(f"  File: {out_path}")
    print(f"  Type: {args.type}")
    print(f"  Prompt ID: {selected_prompt.get('id')}")


def cmd_check(args: argparse.Namespace) -> None:
    """Handle 'check' subcommand: check word count and response section."""
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: Session file not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    words = count_response_words(content)

    target = 100
    if words >= target:
        status = f"[PASS] Met target requirement ({words} words >= {target} words)"
    else:
        status = f"[NEEDS_WORK] Below target ({words}/{target} words)"

    print(f"Session: {file_path.name}")
    print(f"Path:    {file_path}")
    print(f"Words:   {words}")
    print(f"Status:  {status}")


def cmd_stats(args: argparse.Namespace) -> None:
    """Handle 'stats' subcommand: summary of vocab progress, weaknesses, and sessions."""
    print("=======================================================")
    print(" TOEFL Agent Studio Progress & Weakness Summary")
    print("=======================================================")

    max_day = 1
    section_totals: Dict[str, int] = {}
    if VOCAB_SEED_PATH.exists():
        try:
            vocab_items = _load_json_file(VOCAB_SEED_PATH)
            max_day = max((int(v.get("day", 1)) for v in vocab_items if isinstance(v.get("day"), int)), default=1)
            for v in vocab_items:
                sec = v.get("section", "untagged")
                section_totals[sec] = section_totals.get(sec, 0) + 1
            print(f"\n[Vocabulary Bank]")
            print(f"- Total Seed Words: {len(vocab_items)} ({max_day} Days)")
            if section_totals:
                sec_str = ", ".join(f"{k}: {v}" for k, v in sorted(section_totals.items()))
                print(f"- Sections:         {sec_str}")
        except Exception as e:
            print(f"\n[Vocabulary Bank]: Error reading seed: {e}")

    if WEAKNESS_LOG_PATH.exists():
        try:
            log_data = load_weakness_log(WEAKNESS_LOG_PATH)
            missed = log_data.get("missed_vocab", [])
            upgrades = log_data.get("expression_upgrades", [])
            progress = log_data.get("vocab_progress", {})
            active_missed = [m for m in missed if not m.get("mastered", False)]
            mastered_missed = [m for m in missed if m.get("mastered", False)]

            print("\n[Vocab Progress & Weakness Log]")
            print(f"- Current Day:         Day {progress.get('current_day', 1)} / {max_day}")
            print(f"- Completed Days:      {len(progress.get('completed_days', []))} / {max_day}")
            print(f"- Last Studied:        {progress.get('last_studied') or 'Never'}")
            print(f"- Active Missed Words: {len(active_missed)} | Graduated (Mastered): {len(mastered_missed)}")
            print(f"- Expression Upgrades: {len(upgrades)}")

            if active_missed:
                sorted_missed = sorted(
                    active_missed, key=lambda x: x.get("error_count", 0), reverse=True
                )
                print("\n  Top Active Missed Words:")
                for item in sorted_missed[:10]:
                    w = item.get("word", "")
                    cnt = item.get("error_count", 0)
                    sec = item.get("section") or "-"
                    streak = item.get("streak", 0)
                    m = item.get("meaning_ko", "")
                    last = item.get("last_missed", "")
                    print(f"  * {w:<15} [{sec}] (Errors: {cnt}, Streak: {streak}/2) - {m} [Last: {last}]")
        except Exception as e:
            print(f"\n[Weakness Log]: Error reading log: {e}")
    else:
        print("\n[Weakness Log]: No weakness log found yet (data/my_weakness_log.json).")

    if SESSIONS_DIR.exists():
        session_files = [
            f for f in SESSIONS_DIR.glob("*.md") if f.name != ".gitkeep"
        ]
        print("\n[Practice Sessions]")
        print(f"- Total Sessions Created: {len(session_files)}")

        if session_files:
            print("\n  Recent Session Files:")
            for sf in sorted(session_files, reverse=True)[:5]:
                try:
                    wc = count_response_words(sf.read_text(encoding="utf-8"))
                    print(f"  * {sf.name:<35} | Words: {wc}")
                except Exception:
                    print(f"  * {sf.name}")
    else:
        print("\n[Practice Sessions]: No sessions directory found.")

    print("\n=======================================================")


# ----------------------------------------------------------------------
# CLI Entrypoint
# ----------------------------------------------------------------------

def _configure_io_encoding() -> None:
    """Ensure standard streams use UTF-8 on Windows environments."""
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            if hasattr(sys.stderr, "reconfigure"):
                sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drill.py",
        description="TOEFL Agent Studio CLI Trainer (Zero-Dependency)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: today
    parser_today = subparsers.add_parser(
        "today", help="Fetch today's 20 fresh + up to 5 active review words"
    )
    parser_today.add_argument("--day", type=int, help="Target vocabulary day (default: current_day)")
    parser_today.add_argument("--section", choices=VALID_SECTIONS, help="Filter by difficulty tier")
    parser_today.add_argument("--count", type=int, default=20, help="Fresh item count (default: 20)")
    parser_today.add_argument("--max-review", type=int, default=5, help="Max review items (default: 5)")
    parser_today.add_argument("--no-review", action="store_true", help="Exclude missed review items")
    parser_today.add_argument("--json", action="store_true", help="Output compact JSON for agent consumption")
    parser_today.add_argument("--complete", action="store_true", help="Mark target day as completed")

    # Subcommand: record-vocab
    parser_rec = subparsers.add_parser(
        "record-vocab", help="Record missed/passed vocab words and day completion"
    )
    parser_rec.add_argument("--missed", nargs="*", default=[], help="Words missed during drill")
    parser_rec.add_argument("--passed", nargs="*", default=[], help="Review words answered correctly")
    parser_rec.add_argument("--complete-day", type=int, help="Day number to mark completed")

    # Subcommand: ctest
    parser_ctest = subparsers.add_parser(
        "ctest", help="Run Complete the Words vocabulary drills"
    )
    parser_ctest.add_argument("--day", type=int, help="Vocabulary day (default: current_day)")
    parser_ctest.add_argument("--section", choices=VALID_SECTIONS, help="Filter by tier (core, band5, band6)")
    parser_ctest.add_argument(
        "--count", type=int, default=20, help="Number of fresh drill items (default: 20)"
    )
    parser_ctest.add_argument("--review", action="store_true", help="Drill only active missed review words")
    parser_ctest.add_argument("--no-review", action="store_true", help="Exclude review words")
    parser_ctest.add_argument("--json", action="store_true", help="Output JSON instead of formatted text")
    parser_ctest.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive quiz mode in terminal",
    )

    # Subcommand: new-session
    parser_session = subparsers.add_parser(
        "new-session", help="Generate a new Markdown practice worksheet"
    )
    parser_session.add_argument(
        "--type",
        choices=["email", "discussion", "interview", "sentence"],
        default="email",
        help="Prompt type (default: email)",
    )
    parser_session.add_argument(
        "--id",
        type=str,
        help="Specific prompt ID from prompt_bank.json",
    )

    # Subcommand: check
    parser_check = subparsers.add_parser(
        "check", help="Check response word count for a session worksheet"
    )
    parser_check.add_argument(
        "--file",
        required=True,
        type=str,
        help="Path to session markdown file",
    )

    # Subcommand: stats
    subparsers.add_parser(
        "stats", help="Display vocab progress, weakness log, and session statistics"
    )

    return parser


def main() -> None:
    _configure_io_encoding()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "today":
        cmd_today(args)
    elif args.command == "record-vocab":
        cmd_record_vocab(args)
    elif args.command == "ctest":
        cmd_ctest(args)
    elif args.command == "new-session":
        cmd_new_session(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest discover -s tests -p "test_*.py" -v`
Expected: PASS (13 tests OK).

- [ ] **Step 5: Commit Task 2**

```bash
git -C C:\Users\dongwoo\toefl-agent-studio add scripts/drill.py tests/test_drill.py
git -C C:\Users\dongwoo\toefl-agent-studio commit -m "feat(cli): add today, record-vocab, section filtering, and 20-word ctest defaults"
```

---

### Task 3: Curate, Enrich, and Validate 6,000-Word Seed Bank (`data/vocab_seed.json`)

**Files:**
- Modify: `C:\Users\dongwoo\toefl-agent-studio\tests\test_seed_data.py:1-32`
- Modify: `C:\Users\dongwoo\toefl-agent-studio\data\vocab_seed.json`
- Scratch workspace (outside repo): `C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch\`

**Interfaces:**
- Consumes: `mask_word_in_sentence` from `scripts.drill`, existing 24 words from `data/vocab_seed.json`.
- Produces: `data/vocab_seed.json` with `6,000` validated entries (`day` `1..300`, `section` in `{"core", "band5", "band6"}`).

- [ ] **Step 1: Update `tests/test_seed_data.py` with strict 6,000+ invariants (RED)**

Replace `C:\Users\dongwoo\toefl-agent-studio\tests\test_seed_data.py` with:

```python
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
```

- [ ] **Step 2: Run `test_seed_data` to verify it fails on the 24-word seed (RED)**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest tests.test_seed_data -v`
Expected: FAIL with `AssertionError: 24 not greater than or equal to 6000`.

- [ ] **Step 3: Build the deterministic 6,000-word master pool from verified open corpora (in scratch)**

Write `C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch\build_master_pool.py` to download, normalize, deduplicate, and slot 6,000 unique headwords (`2,000` each for `core`, `band5`, `band6`) across Days `1..300`:

```python
import csv
import io
import json
import re
import urllib.request
from pathlib import Path

SCRATCH = Path(r"C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch")
SEED_PATH = Path(r"C:\Users\dongwoo\toefl-agent-studio\data\vocab_seed.json")
BATCH_DIR = SCRATCH / "vocab_batches"
BATCH_DIR.mkdir(parents=True, exist_ok=True)

URLS = {
    "cefrj": "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/cefrj-vocabulary-profile-1.5.csv",
    "c1c2": "https://raw.githubusercontent.com/openlanguageprofiles/olp-en-cefrj/master/octanove-vocabulary-profile-c1c2-1.0.csv",
    "ngsl": "https://raw.githubusercontent.com/koba-ninkigumi/ngsl/master/NGSL-1.01.csv",
    "nawl": "https://raw.githubusercontent.com/koba-ninkigumi/ngsl/master/NAWL-1.0.csv",
    "toefl": "https://raw.githubusercontent.com/KyleBing/english-vocabulary/master/json/6-%E6%89%98%E7%A6%8F-%E9%A1%BA%E5%BA%8F.json",
}

ORIGINAL_TIERS = {
    "comprehensive": "core", "constitute": "core", "correlation": "core",
    "differentiate": "core", "imply": "core", "inevitable": "core",
    "peculiar": "core", "profound": "core", "scarcity": "core", "viable": "core",
    "ambiguous": "band5", "arbitrary": "band5", "discrepancy": "band5",
    "eradicate": "band5", "exemplify": "band5", "fluctuate": "band5",
    "mitigate": "band5", "pivotal": "band5", "pragmatic": "band5",
    "substantiate": "band5", "unprecedented": "band5",
    "anomalous": "band6", "assuage": "band6", "ubiquitous": "band6",
}

VALID_SHORT_ACADEMIC = {"aid", "aim", "apt", "awe", "ban", "bid", "cue", "due", "era", "fee", "gap", "hub", "law", "odd", "opt", "owe", "raw", "sum", "tax", "via", "vow", "wan"}
POS_MAP = {"n": "noun", "v": "verb", "adj": "adjective", "adv": "adverb", "noun": "noun", "verb": "verb", "adjective": "adjective", "adverb": "adverb"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def clean_word(w: str) -> bool:
    return bool(re.fullmatch(r"[a-z]{3,20}", w)) and (len(w) >= 4 or w in VALID_SHORT_ACADEMIC)


def main() -> None:
    original_items = {x["word"].lower(): x for x in json.loads(SEED_PATH.read_text(encoding="utf-8"))}

    inflection_to_lemma = {}
    ngsl_lemmas, nawl_lemmas = [], []
    for key, target in (("ngsl", ngsl_lemmas), ("nawl", nawl_lemmas)):
        for row in csv.reader(io.StringIO(fetch(URLS[key]))):
            forms = [c.strip().lower() for c in row if c.strip()]
            if not forms:
                continue
            lemma = forms[0]
            if clean_word(lemma):
                target.append(lemma)
            for f in forms:
                inflection_to_lemma[f] = lemma

    cefr_pos = {}
    cefr_by_level = {"A2": [], "B1": [], "B2": [], "C1": [], "C2": []}
    for key in ("cefrj", "c1c2"):
        reader = csv.DictReader(io.StringIO(fetch(URLS[key])))
        for row in reader:
            hw = row["headword"].split("/")[0].strip().lower()
            pos = POS_MAP.get(row.get("pos", "").strip().lower())
            lvl = row.get("CEFR", "").strip().upper()
            if clean_word(hw) and pos and lvl in cefr_by_level:
                cefr_pos.setdefault(hw, pos)
                cefr_by_level[lvl].append((hw, pos))

    toefl_raw = json.loads(fetch(URLS["toefl"]))
    toefl_words = []
    for entry in toefl_raw:
        w = entry.get("word", "").strip().lower()
        trans = entry.get("translations") or []
        pos = next((POS_MAP[t.get("type", "").lower()] for t in trans if t.get("type", "").lower() in POS_MAP), None)
        if clean_word(w) and pos:
            toefl_words.append((w, pos))
    toefl_set = {w for w, _ in toefl_words}

    used = set(ORIGINAL_TIERS.keys())
    tiers = {"core": [], "band5": [], "band6": []}

    for w, sec in ORIGINAL_TIERS.items():
        orig = original_items[w]
        tiers[sec].append({
            "word": w, "pos": orig["pos"], "section": sec, "pre_filled": orig,
        })

    def add_candidate(sec: str, w: str, pos: str) -> None:
        lemma = inflection_to_lemma.get(w, w)
        if not clean_word(lemma) or lemma in used or w in used or len(tiers[sec]) >= 2000:
            return
        used.add(lemma)
        used.add(w)
        tiers[sec].append({"word": w, "pos": pos, "section": sec})

    # Core (2,000): CEFR B1/B2 + NGSL
    for w, pos in cefr_by_level["B1"] + cefr_by_level["B2"]:
        if w in toefl_set or w in set(ngsl_lemmas):
            add_candidate("core", w, pos)
    for w in ngsl_lemmas:
        if w in cefr_pos:
            add_candidate("core", w, cefr_pos[w])
    for w, pos in cefr_by_level["B1"] + cefr_by_level["A2"]:
        add_candidate("core", w, pos)

    # Band 5.0 (2,000): NAWL + CEFR B2/C1 intersecting TOEFL
    c2_set = {x for x, _ in cefr_by_level["C2"]}
    for w in nawl_lemmas:
        add_candidate("band5", w, cefr_pos.get(w, "noun"))
    for w, pos in cefr_by_level["B2"] + cefr_by_level["C1"]:
        if w in toefl_set:
            add_candidate("band5", w, pos)
    for w, pos in toefl_words:
        if w not in c2_set:
            add_candidate("band5", w, pos)

    # Band 6.0 (2,000): Octanove C1/C2 + advanced TOEFL
    for w, pos in cefr_by_level["C2"] + cefr_by_level["C1"]:
        add_candidate("band6", w, pos)
    for w, pos in reversed(toefl_words):
        add_candidate("band6", w, pos)

    assert all(len(tiers[s]) == 2000 for s in tiers), {s: len(tiers[s]) for s in tiers}

    # Assign Days 1..300 in exact 7/7/6 3-day rotation
    rotation = {1: (7, 7, 6), 2: (7, 6, 7), 0: (6, 7, 7)}
    idx_map = {"core": 0, "band5": 0, "band6": 0}
    slots = []
    for day in range(1, 301):
        c_cnt, b5_cnt, b6_cnt = rotation[day % 3]
        day_items = []
        for sec, cnt in (("core", c_cnt), ("band5", b5_cnt), ("band6", b6_cnt)):
            start = idx_map[sec]
            day_items.extend(tiers[sec][start : start + cnt])
            idx_map[sec] = start + cnt
        for pos_idx, item in enumerate(day_items, 1):
            item["day"] = day
            item["id"] = f"day{day:03d}_{pos_idx:03d}"
            slots.append(item)

    batch_size = 40
    for b_idx in range(len(slots) // batch_size):
        chunk = slots[b_idx * batch_size : (b_idx + 1) * batch_size]
        (BATCH_DIR / f"batch_{b_idx+1:03d}.json").write_text(
            json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"Prepared {len(slots)} slots across {len(slots) // batch_size} batches.")


if __name__ == "__main__":
    main()
```

Run: `python "C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch\build_master_pool.py"`
Expected: `Prepared 6000 slots across 150 batches.`

- [ ] **Step 4: Parallel batch enrichment via `run_workflow` + automated validation/repair**

Write `C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch\enrich_vocab_workflow.py` and execute via `run_workflow` (processing 40 entries per batch so output stays well within single-response token limits):

```python
import json
from pathlib import Path

SCRATCH = Path(r"C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch")
BATCH_DIR = SCRATCH / "vocab_batches"
OUT_DIR = SCRATCH / "enriched_batches"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ITEM_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "day", "section", "word", "pos", "meaning_ko", "synonyms", "example", "collocations"],
        "properties": {
            "id": {"type": "string"},
            "day": {"type": "integer"},
            "section": {"type": "string"},
            "word": {"type": "string"},
            "pos": {"type": "string"},
            "meaning_ko": {"type": "string"},
            "synonyms": {"type": "array", "items": {"type": "string"}},
            "example": {"type": "string"},
            "collocations": {"type": "array", "items": {"type": "string"}},
        },
    },
}

batch_files = sorted(BATCH_DIR.glob("batch_*.json"))


async def process_batch(batch_path: Path) -> str:
    out_path = OUT_DIR / batch_path.name
    if out_path.exists():
        return f"SKIP {batch_path.name}"
    items = json.loads(batch_path.read_text(encoding="utf-8"))
    pre_filled = {x["id"]: {**x["pre_filled"], "id": x["id"], "day": x["day"], "section": x["section"]} for x in items if "pre_filled" in x}
    to_enrich = [{"id": x["id"], "day": x["day"], "section": x["section"], "word": x["word"], "pos": x["pos"]} for x in items if "pre_filled" not in x]

    enriched = []
    if to_enrich:
        prompt = (
            "Enrich each TOEFL vocabulary entry in the JSON array below.\n"
            "Rules:\n"
            "1. Preserve id, day, section, word, pos exactly.\n"
            "2. meaning_ko: concise natural Korean meanings (2-3 senses comma-separated).\n"
            "3. synonyms: 3 distinct academic English synonyms (never repeat word itself).\n"
            "4. example: 1 natural TOEFL-style academic sentence containing the EXACT uninflected word as a standalone token matching \\bword\\b.\n"
            "5. collocations: 3 natural academic collocations using the word.\n\n"
            f"Input:\n{json.dumps(to_enrich, ensure_ascii=False)}"
        )
        enriched = await agent(prompt, schema=ITEM_SCHEMA, model="flash", role=f"Enrich {batch_path.name}")

    merged = sorted(list(pre_filled.values()) + enriched, key=lambda x: x["id"])
    out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"OK {batch_path.name}: {len(merged)}"


phase("Enrich 60 Batches")
results = await parallel(batch_files, process_batch)
for r in results:
    log(r)
```

Then write and run `C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch\validate_and_merge.py`:

```python
import json
import re
from pathlib import Path

SCRATCH = Path(r"C:\Users\dongwoo\.gemini\antigravity\brain\f5accfea-0a5e-409b-9bd4-88e0e2121675\scratch")
OUT_DIR = SCRATCH / "enriched_batches"
SEED_PATH = Path(r"C:\Users\dongwoo\toefl-agent-studio\data\vocab_seed.json")

all_items = []
for f in sorted(OUT_DIR.glob("batch_*.json")):
    all_items.extend(json.loads(f.read_text(encoding="utf-8")))

invalid = []
for item in all_items:
    w = item.get("word", "").strip()
    ex = item.get("example", "")
    syns = [s.strip().lower() for s in item.get("synonyms", []) if s.strip()]
    cols = [c.strip() for c in item.get("collocations", []) if c.strip()]
    if (
        not item.get("meaning_ko", "").strip()
        or len(syns) < 2
        or w.lower() in syns
        or len(cols) < 2
        or not re.search(rf"\b{re.escape(w)}\b", ex, re.IGNORECASE)
    ):
        invalid.append(item)

if invalid:
    (SCRATCH / "repair_needed.json").write_text(json.dumps(invalid, ensure_ascii=False, indent=2), encoding="utf-8")
    raise SystemExit(f"Found {len(invalid)} invalid entries written to repair_needed.json")

all_items.sort(key=lambda x: (x["day"], x["id"]))
SEED_PATH.write_text(json.dumps(all_items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Merged {len(all_items)} validated entries into {SEED_PATH}")
```

If `repair_needed.json` is emitted, fix/re-enrich only the items in `repair_needed.json` via a targeted `run_workflow` pass, patch them back into their `enriched_batches/batch_XXX.json`, and re-run `validate_and_merge.py` until `Merged 6000 validated entries` succeeds with exit code 0.

- [ ] **Step 5: Run full seed & drill test suite to verify GREEN**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest discover -s tests -p "test_*.py" -v`
Expected: PASS (all seed + drill + skills tests OK).

- [ ] **Step 6: Commit Task 3**

```bash
git -C C:\Users\dongwoo\toefl-agent-studio add data/vocab_seed.json tests/test_seed_data.py
git -C C:\Users\dongwoo\toefl-agent-studio commit -m "feat(data): expand vocab_seed.json to 6000 tiered academic words across 300 days"
```

---

### Task 4: Update Skills (`toefl-vocab`, `toefl-speaking`, `toefl-writing`), Repo Docs, and Skill Integrity Tests

**Files:**
- Modify: `C:\Users\dongwoo\toefl-agent-studio\tests\test_skills_integrity.py:1-20`
- Modify: `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-vocab\SKILL.md:1-81`
- Modify: `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-speaking\SKILL.md:1-90`
- Modify: `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-writing\SKILL.md:1-102`
- Modify: `C:\Users\dongwoo\toefl-agent-studio\AGENTS.md:1-109`
- Modify: `C:\Users\dongwoo\toefl-agent-studio\README.md:1-137`

**Interfaces:**
- Consumes: `today --json`, `record-vocab`, `ctest`, `stats` CLI subcommands from Task 2 and `data/vocab_seed.json` from Task 3.
- Produces: Updated `SKILL.md` instructions enforcing `today --json` (no full `read_file` on `vocab_seed.json`), 3-round section mini-batch UX, repo-root fallback, and updated `AGENTS.md` / `README.md`.

- [ ] **Step 1: Update `tests/test_skills_integrity.py` with new skill contract checks (RED)**

Replace `C:\Users\dongwoo\toefl-agent-studio\tests\test_skills_integrity.py` with:

```python
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run `test_skills_integrity` to verify it fails (RED)**

Run: `Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest tests.test_skills_integrity -v`
Expected: FAIL (`'today --json' not found`).

- [ ] **Step 3: Rewrite `.agents/skills/toefl-vocab/SKILL.md` and add repo-root fallback to `toefl-speaking` and `toefl-writing`**

Replace `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-vocab\SKILL.md` with:

```markdown
---
name: toefl-vocab
description: Use when the user triggers $toefl-vocab or requests a 2026 Revised TOEFL iBT daily vocabulary drill combining 20 tiered words (core, band5, band6) plus active weakness reviews across Complete the Words, synonym matching, and collocation production.
---

# TOEFL Vocab Mastery Skill (`toefl-vocab`)

## Purpose
Administer a structured daily **20-word (+ up to 5 active review words)** vocabulary drill tailored for the **2026 Revised TOEFL iBT** (`Complete the Words`, academic synonym precision, and collocation production) in a stealth IDE workflow.

---

## Repository Resolution & Context Guardrail

1. **Repo Root Resolution**:
   - Check if `data/vocab_seed.json` and `scripts/drill.py` exist in the current working directory (`./`). If so, run commands from `./` (preserving work-PC `git clone` portability).
   - Otherwise (when invoked globally from another workspace on the home PC), use `~/toefl-agent-studio` (`C:\Users\dongwoo\toefl-agent-studio`) as the working directory for all commands and log paths.
2. **CRITICAL — Never Open `data/vocab_seed.json` Directly**:
   - `data/vocab_seed.json` holds **6,000+ words (300+ days)**. NEVER call `read_file` or dump the full JSON file.
   - Always fetch today's slice via CLI:
     ```bash
     python scripts/drill.py today --json
     ```
     (Supports optional `--day N` and `--section core|band5|band6` when the user specifies a day or tier.)

---

## 3-Round Section Mini-Batch Workflow

When the user triggers `$toefl-vocab` or asks for a vocabulary drill:

### Step 1: Load Today's Bundle (20 Fresh + Up to 5 Active Reviews)
Run `python scripts/drill.py today --json` to retrieve:
- `day` and `max_day`
- `fresh_items` (20 words grouped across `core`, `band5`, `band6`)
- `review_items` (up to 5 unmastered words from `data/my_weakness_log.json`, sorted by `error_count`)

Announce today's scope concisely (e.g., `Day X / 300 — 신규 20단어 (Core · Band 5.0 · Band 6.0) + 오답 복습 N단어`) and proceed immediately to **Round 1**.

### Step 2: Section Mini-Batches (Rounds 1 -> 2 -> 3)
Run three interactive rounds, **waiting for user answers after each round** and giving immediate Korean feedback before moving to the next round:

- **Round 1 — `Core` (6–7 fresh words + matching/untagged review words)**
- **Round 2 — `Band 5.0` (6–7 fresh words + `band5` review words)**
- **Round 3 — `Band 6.0` (6–7 fresh words + `band6` review words)**

For **each round**, present two compact parts together:
1. **Part A: Complete the Words** — Use `masked_example` (2-char prefix for length <= 5, 3-char prefix for length >= 6) with `[pos]` and optional `[REVIEW]` badge.
2. **Part B: Synonym Match** — List the round's words and shuffled synonym clusters (`[syn1 / syn2]`) for quick matching.

When the user submits answers for the round:
- Grade spelling (Part A) and semantic match (Part B) concisely.
- Give brief Korean explanations, meaning/nuance notes, and high-value collocations for any missed item.
- Keep track of `missed_words` (any missed fresh or review item) and `passed_review_words` (any review item answered accurately in this session).

### Step 3: Final Round — Collocation Production (2–3 Sentences)
Select **2–3 high-impact collocations** from today's `band5` and `band6` words and ask the user to write **2–3 original academic sentences**.
- Grade syntax, preposition usage, and academic register with brief Korean feedback.
- If any sentence contains awkward Konglish or phrasing errors, prepare an entry for `expression_upgrades` in `data/my_weakness_log.json`.

---

## Mandatory State & Weakness Logging

At session wrap-up:
1. Run the deterministic state sync command:
   ```bash
   python scripts/drill.py record-vocab --missed <word1> ... --passed <rev1> ... --complete-day <day>
   ```
   *(Omit `--missed` or `--passed` if empty; omit `--complete-day` if filtering by a single `--section` without finishing the day.)*
   - Every missed word increments `error_count` and resets `streak = 0`, `mastered = false`.
   - Every passed review word increments `streak`; at `streak >= 2`, the word graduates (`mastered = true`).
2. Append any Phase/Final Round sentence upgrades to `expression_upgrades` in `data/my_weakness_log.json`.
3. Display final summary:
   - Score breakdown (`Core`, `Band 5.0`, `Band 6.0`, `Review`)
   - Newly logged missed words vs graduated (`mastered`) words
   - Updated progress (`Day D / 300`) and CLI reminder: `python scripts/drill.py stats`
```

Add the **Repository Resolution** section right after `## Purpose` in both:
- `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-speaking\SKILL.md`
- `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-writing\SKILL.md`

```markdown
## Repository Resolution
- Prefer the current working directory (`./`) when `data/prompt_bank.json` and `scripts/drill.py` are present (preserving work-PC `git clone` portability).
- When invoked globally from another workspace on the home PC, resolve `data/`, `sessions/`, and `scripts/drill.py` under `~/toefl-agent-studio` (`C:\Users\dongwoo\toefl-agent-studio`).
```

- [ ] **Step 4: Update `AGENTS.md` and `README.md`**

Update `C:\Users\dongwoo\toefl-agent-studio\AGENTS.md`:
- Line 50 (`$toefl-vocab` table row): update to describe daily **20 fresh words (Core / Band 5.0 / Band 6.0) + up to 5 active reviews**, 3-round section mini-batches, collocation production, and `today --json` + `record-vocab`.
- Lines 102–109 (`scripts/drill.py` section): add `python scripts/drill.py today --json`, `python scripts/drill.py record-vocab --missed ... --passed ... --complete-day N`, and update `ctest` example to `--count 20 --section band5`.

Update `C:\Users\dongwoo\toefl-agent-studio\README.md`:
- Update Morning Vocab Warmup routine row to `20 fresh + up to 5 review words` via `$toefl-vocab` or `python scripts/drill.py today` / `ctest --count 20`.
- Update `CLI Trainer Reference` with `today`, `record-vocab`, updated `ctest` (`--section core|band5|band6`, `--count 20`, `--review`), and `stats` (`Day X / 300`).
- Update `data/vocab_seed.json` description (`6,000+ tiered academic words across 300 days: Core, Band 5.0, Band 6.0`) and `tests/test_*.py` description.

- [ ] **Step 5: Run full test suite and CLI smoke checks**

Run:
`Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest discover -s tests -p "test_*.py" -v`
`python scripts/drill.py today --json`
`python scripts/drill.py stats`
Expected: All unit tests PASS; `today --json` prints valid JSON with 20 fresh items (`core` + `band5` + `band6`); `stats` prints `6000` words (`300 Days`, `band5: 2000, band6: 2000, core: 2000`).

- [ ] **Step 6: Commit Task 4**

```bash
git -C C:\Users\dongwoo\toefl-agent-studio add .agents/skills/toefl-vocab/SKILL.md .agents/skills/toefl-speaking/SKILL.md .agents/skills/toefl-writing/SKILL.md AGENTS.md README.md tests/test_skills_integrity.py
git -C C:\Users\dongwoo\toefl-agent-studio commit -m "feat(skills): update toefl-vocab for 20-word 3-section mini-batches and add global path fallback"
```

---

### Task 5: Home PC Global Skill Junctions (`~/.agents`) & Obsidian Spec/Dashboard Sync

**Files:**
- Modify: `C:\Users\dongwoo\.agents\.gitignore:1-13`
- Modify: `C:\Users\dongwoo\.agents\scripts\sync-agent-links.ps1:31-45`
- Modify: `C:\Users\dongwoo\OneDrive - 경희대학교\Obsidian\20_Projects\[어학] 토익_오픽_토플\03_토플\03_사내PC_토플_에이전트_스튜디오_스펙.md`
- Modify: `C:\Users\dongwoo\OneDrive - 경희대학교\Obsidian\20_Projects\[어학] 토익_오픽_토플\03_토플\00_토플_마스터_대시보드.md`

**Interfaces:**
- Consumes: Finalized skill folders in `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\{toefl-vocab,toefl-speaking,toefl-writing}` and Obsidian MCP `knowledge-index-sync`.
- Produces: Directory junctions across `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`, `~/.gemini/skills`, and up-to-date Obsidian spec/dashboard notes.

- [ ] **Step 1: Register TOEFL project skill junctions in `C:\Users\dongwoo\.agents\.gitignore` and `sync-agent-links.ps1`**

Append to `C:\Users\dongwoo\.agents\.gitignore`:

```gitignore
skills/toefl-vocab
skills/toefl-speaking
skills/toefl-writing
```

Update `C:\Users\dongwoo\.agents\scripts\sync-agent-links.ps1` right after the `querying-obsidian-knowledge` block (lines 33–40):

```powershell
$ToeflSkills = @("toefl-vocab", "toefl-speaking", "toefl-writing")
foreach ($skill in $ToeflSkills) {
    $ToeflSkillSource = Join-Path $UserHome "toefl-agent-studio\.agents\skills\$skill"
    $ToeflSkillTarget = Join-Path $SkillsDir $skill
    if ((Test-Path $ToeflSkillSource) -and -not (Test-Path $ToeflSkillTarget)) {
        Write-Host "Linking local project skill: $skill" -ForegroundColor Yellow
        New-Item -ItemType Junction -Path $ToeflSkillTarget -Target $ToeflSkillSource | Out-Null
    }
}
```

- [ ] **Step 2: Run `sync-agent-links.ps1` and verify junctions across all agent runtimes**

Run:
`pwsh -ExecutionPolicy Bypass -File C:\Users\dongwoo\.agents\scripts\sync-agent-links.ps1`
`Get-Item C:\Users\dongwoo\.agents\skills\toefl-*, C:\Users\dongwoo\.gemini\skills\toefl-*, C:\Users\dongwoo\.claude\skills\toefl-*, C:\Users\dongwoo\.codex\skills\toefl-* | Select-Object FullName, LinkType, Target`
Expected: All 3 skills appear as `Junction` pointing to `C:\Users\dongwoo\toefl-agent-studio\.agents\skills\toefl-*`.

- [ ] **Step 3: Commit `.agents` sync changes**

```bash
git -C C:\Users\dongwoo\.agents add .gitignore scripts/sync-agent-links.ps1
git -C C:\Users\dongwoo\.agents commit -m "chore(sync): link toefl-agent-studio skills via junction"
```

- [ ] **Step 4: Update Obsidian spec and dashboard notes, then sync RAG index**

1. Update `C:\Users\dongwoo\OneDrive - 경희대학교\Obsidian\20_Projects\[어학] 토익_오픽_토플\03_토플\03_사내PC_토플_에이전트_스튜디오_스펙.md`:
   - Section `3.1 A. data/vocab_seed.json`: update from `Day 1~20` to `6,000+단어 (Day 1~300, 티어별 core/band5/band6 각 2,000개, 3일 주기 7/7/6 로테이션)` and add `"section"` field to the example JSON.
   - Section `3.1 C. data/my_weakness_log.json`: document `vocab_progress` and `streak`/`mastered` graduation.
   - Section `3.2` & `3.3`: update `today --json`, `record-vocab`, `ctest --count 20 --section`, `$toefl-vocab` 3-round mini-batch workflow, and mark `- [x] 집 PC toefl-agent-studio 일일 단어 학습량 20개+ 설정 업데이트` complete.
2. Update `C:\Users\dongwoo\OneDrive - 경희대학교\Obsidian\20_Projects\[어학] 토익_오픽_토플\03_토플\00_토플_마스터_대시보드.md`:
   - Add update bullet recording completion of the home PC `toefl-agent-studio` 6,000-word / 3-tier / daily 20+ word expansion and global skill linking.
3. Call `call_mcp_tool(ServerName="obsidian_knowledge", ToolName="knowledge-index-sync", Arguments={})`.

- [ ] **Step 5: Final end-to-end verification**

Run:
`Set-Location C:\Users\dongwoo\toefl-agent-studio; python -m unittest discover -s tests -p "test_*.py" -v`
`git -C C:\Users\dongwoo\toefl-agent-studio status -sb`
`git -C C:\Users\dongwoo\.agents status -sb`
Expected: All tests pass, `toefl-agent-studio` working tree is clean (`ahead` of `origin/main`, ready for user-requested push so work PC can `git pull`).

---

## Plan Self-Review

- **Spec coverage**:
  - 6,000+ words, `core`/`band5`/`band6` tiers, 300 days × 20 words, `7/7/6` rotation, 24 seed words preserved -> Task 3
  - `my_weakness_log.json` backward compatibility, `vocab_progress`, 2-streak graduation, reset on miss -> Task 1
  - `today --json`, `record-vocab`, `ctest` default 20 + `--section` + `--review`, `stats` -> Task 2
  - `$toefl-vocab` 3-round mini-batches, `vocab_seed.json` read guardrail, path fallback across all 3 skills, `AGENTS.md`/`README.md` -> Task 4
  - `~/.agents` junctions + Obsidian spec/dashboard + `knowledge-index-sync` -> Task 5
- **Placeholder scan**: All code blocks for `scripts/drill.py`, `tests/test_drill.py`, `tests/test_seed_data.py`, `tests/test_skills_integrity.py`, `SKILL.md` files, and `sync-agent-links.ps1` are complete and explicit.
- **Type & signature consistency**: Verified identical names across Tasks 1–4 (`load_weakness_log`, `save_weakness_log`, `record_missed_vocab`, `record_correct_vocab`, `mark_day_completed`, `select_daily_vocab`, `cmd_today`, `cmd_record_vocab`, `cmd_ctest`, `cmd_stats`, `VALID_SECTIONS`).
