#!/usr/bin/env python3
"""TOEFL Agent Studio CLI Trainer.

Zero-dependency standard-library CLI for TOEFL 2026 preparation:
- Complete the Words drills (CTEST)
- Worksheet session generator (email, academic discussion, interview)
- Word count and response checker
- Weakness log & session stats summary
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SESSIONS_DIR = REPO_ROOT / "sessions"
VOCAB_SEED_PATH = DATA_DIR / "vocab_seed.json"
PROMPT_BANK_PATH = DATA_DIR / "prompt_bank.json"
WEAKNESS_LOG_PATH = DATA_DIR / "my_weakness_log.json"
VALID_SECTIONS = ("core", "band5", "band6")


# ----------------------------------------------------------------------
# Core Pure Functions (Tested)
# ----------------------------------------------------------------------

def mask_word_in_sentence(sentence: str, word: str) -> str:
    """Mask a word in a sentence for Complete the Words (CTEST) drills.

    Preserves the first 2 characters if len(word) <= 5,
    or the first 3 characters if len(word) >= 6, and replaces
    the remaining characters with underscores ('_').
    Case-insensitive word match preserves original leading casing.
    """
    if not word:
        return sentence

    word_len = len(word)
    keep = 2 if word_len <= 5 else 3

    def _replace_match(match: re.Match[str]) -> str:
        matched = match.group(0)
        prefix = matched[:keep]
        masked = prefix + "_" * (len(matched) - keep)
        return masked

    pattern = re.compile(rf"\b{re.escape(word)}\b", flags=re.IGNORECASE)
    return pattern.sub(_replace_match, sentence)


def count_response_words(markdown_text: str) -> int:
    """Extract text under '## ✍️ My Response' and count whitespace-separated words.

    Strips any HTML comments (<!-- ... -->) before counting.
    Stops extracting when the next '## ' heading or end of file is reached.
    """
    normalized = markdown_text.replace("\r\n", "\n")
    pattern = re.compile(
        r"^##\s+(?:✍️\s*)?My Response[^\S\n]*\n(.*?)(?=^##\s|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(normalized)
    if not match:
        return 0

    section_text = match.group(1)
    # Strip HTML comments
    clean_text = re.sub(r"<!--.*?-->", "", section_text, flags=re.DOTALL)
    words = clean_text.split()
    return len(words)


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


def _format_prompt_details(prompt_type: str, prompt_data: Dict[str, Any]) -> str:
    """Format prompt data dictionary into clean Markdown section."""
    ptype = prompt_type.lower()
    lines: List[str] = []

    if ptype in ("email", "write_an_email"):
        if "title" in prompt_data:
            lines.append(f"### {prompt_data['title']}\n")
        if "scenario" in prompt_data:
            lines.append(f"**Scenario**:\n{prompt_data['scenario']}\n")
        if "recipient" in prompt_data:
            lines.append(f"- **Recipient**: {prompt_data['recipient']}")
        if "subject" in prompt_data:
            lines.append(f"- **Subject**: {prompt_data['subject']}")
        if "bullet_points" in prompt_data and prompt_data["bullet_points"]:
            lines.append("\n**Requirements**:")
            for bp in prompt_data["bullet_points"]:
                lines.append(f"- {bp}")

    elif ptype in ("discussion", "academic_discussion"):
        if "course" in prompt_data:
            lines.append(f"**Course**: {prompt_data['course']}\n")
        if "professor_question" in prompt_data:
            lines.append(f"**Professor's Question**:\n{prompt_data['professor_question']}\n")
        if "student_a" in prompt_data:
            sa = prompt_data["student_a"]
            if isinstance(sa, dict):
                lines.append(f"- **{sa.get('name', 'Student A')}**: {sa.get('stance', '')}")
            else:
                lines.append(f"- **Student A**: {sa}")
        if "student_b" in prompt_data:
            sb = prompt_data["student_b"]
            if isinstance(sb, dict):
                lines.append(f"- **{sb.get('name', 'Student B')}**: {sb.get('stance', '')}")
            else:
                lines.append(f"- **Student B**: {sb}")

    elif ptype in ("interview", "take_an_interview"):
        if "topic" in prompt_data:
            lines.append(f"**Topic**: {prompt_data['topic']}\n")
        if "context" in prompt_data:
            lines.append(f"**Context**:\n{prompt_data['context']}\n")
        if "questions" in prompt_data and prompt_data["questions"]:
            lines.append("**Questions**:")
            for i, q in enumerate(prompt_data["questions"], 1):
                lines.append(f"{i}. {q}")
        if "model_expressions" in prompt_data and prompt_data["model_expressions"]:
            lines.append("\n**Model Expressions to Consider**:")
            for exp in prompt_data["model_expressions"]:
                lines.append(f"- {exp}")

    elif ptype in ("sentence", "build_a_sentence"):
        if "context_sentence" in prompt_data:
            lines.append(f"**Target Sentence**:\n{prompt_data['context_sentence']}\n")
        if "scrambled_chunks" in prompt_data and prompt_data["scrambled_chunks"]:
            lines.append("**Scrambled Chunks**:")
            for chunk in prompt_data["scrambled_chunks"]:
                lines.append(f"- {chunk}")

    else:
        for k, v in prompt_data.items():
            if k in ("id", "sample_answer"):
                continue
            if isinstance(v, list):
                lines.append(f"**{k}**:")
                for item in v:
                    lines.append(f"- {item}")
            elif isinstance(v, dict):
                lines.append(f"**{k}**:")
                for dk, dv in v.items():
                    lines.append(f"- **{dk}**: {dv}")
            else:
                lines.append(f"**{k}**: {v}")

    return "\n".join(lines).strip()


def create_session_file(
    session_dir: Path,
    prompt_type: str,
    prompt_data: Dict[str, Any],
    now_str: str,
) -> Path:
    """Create a Markdown practice session worksheet file.

    File name format: {YYYY-MM-DD}_{prompt_type}_{prompt_id}.md
    """
    session_dir = Path(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)

    date_prefix = now_str[:10]
    prompt_id = prompt_data.get("id", "custom")
    filename = f"{date_prefix}_{prompt_type}_{prompt_id}.md"
    out_path = session_dir / filename

    prompt_details = _format_prompt_details(prompt_type, prompt_data)

    content = (
        f"# TOEFL Practice Session ({prompt_type})\n\n"
        f"- **Started At**: {now_str}\n"
        f"- **Prompt ID**: {prompt_id}\n\n"
        f"## 📋 Prompt\n\n"
        f"{prompt_details}\n\n"
        f"## ✍️ My Response\n\n"
        f"<!-- Write your response here. Word count target: 100+ words. -->\n\n"
        f"## 📊 AI Evaluation\n\n"
        f"Pending evaluation.\n"
    )

    out_path.write_text(content, encoding="utf-8")
    return out_path


# ----------------------------------------------------------------------
# CLI Subcommand Handlers
# ----------------------------------------------------------------------

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
