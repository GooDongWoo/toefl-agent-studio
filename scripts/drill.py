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


def record_missed_vocab(
    log_path: Path, word: str, meaning_ko: str, today_iso: str
) -> Dict[str, Any]:
    """Record a missed vocabulary word into the weakness JSON log.

    If word exists (case-insensitive), increments error_count and updates last_missed.
    Otherwise appends a new entry.
    """
    log_path = Path(log_path)
    data: Dict[str, Any] = {"missed_vocab": [], "expression_upgrades": []}

    if log_path.exists():
        try:
            content = log_path.read_text(encoding="utf-8")
            loaded = json.loads(content)
            if isinstance(loaded, dict):
                data = loaded
                if "missed_vocab" not in data or not isinstance(data["missed_vocab"], list):
                    data["missed_vocab"] = []
                if "expression_upgrades" not in data:
                    data["expression_upgrades"] = []
        except Exception:
            data = {"missed_vocab": [], "expression_upgrades": []}

    target_word = word.strip().lower()
    found = False
    for item in data["missed_vocab"]:
        if item.get("word", "").strip().lower() == target_word:
            item["error_count"] = item.get("error_count", 0) + 1
            item["last_missed"] = today_iso
            if meaning_ko and not item.get("meaning_ko"):
                item["meaning_ko"] = meaning_ko
            found = True
            break

    if not found:
        data["missed_vocab"].append(
            {
                "word": word.strip(),
                "meaning_ko": meaning_ko.strip(),
                "error_count": 1,
                "last_missed": today_iso,
            }
        )

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
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


def cmd_ctest(args: argparse.Namespace) -> None:
    """Handle 'ctest' subcommand: Complete the Words drill."""
    vocab_items: List[Dict[str, Any]] = _load_json_file(VOCAB_SEED_PATH)

    if args.day is not None:
        vocab_items = [v for v in vocab_items if v.get("day") == args.day]

    if not vocab_items:
        print(f"No vocabulary items found for day {args.day}.")
        return

    selected = vocab_items[: args.count]
    today_iso = datetime.now().strftime("%Y-%m-%d")

    if args.interactive:
        print(f"\n=======================================================")
        print(f" TOEFL Complete the Words Drill (Interactive Quiz)")
        print(f" Items: {len(selected)} | Day: {args.day or 'All'}")
        print(f"=======================================================\n")
        score = 0
        for i, item in enumerate(selected, 1):
            word = item["word"]
            masked = mask_word_in_sentence(item["example"], word)
            print(f"[{i}/{len(selected)}] [{item.get('pos', '')}] {item.get('meaning_ko', '')}")
            print(f"Context: {masked}")
            try:
                user_ans = input("Your answer: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nQuiz interrupted.")
                break

            if user_ans.lower() == word.lower():
                print(" -> [CORRECT]\n")
                score += 1
            else:
                print(f" -> [INCORRECT] Correct answer: {word}\n")
                record_missed_vocab(
                    WEAKNESS_LOG_PATH,
                    word,
                    item.get("meaning_ko", ""),
                    today_iso,
                )

        print(f"--- Drill Complete: {score}/{len(selected)} correct ---")
        if score < len(selected):
            print(f"Missed words logged to {WEAKNESS_LOG_PATH}")
    else:
        day_str = f"Day {args.day}" if args.day is not None else "All Days"
        print(f"\n=== TOEFL Complete the Words Drill ({day_str}, Count: {len(selected)}) ===\n")
        for i, item in enumerate(selected, 1):
            word = item["word"]
            masked = mask_word_in_sentence(item["example"], word)
            synonyms = ", ".join(item.get("synonyms", []))
            print(f"{i}. [{item.get('pos', '')}] {item.get('meaning_ko', '')}")
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
        # Default to first available prompt
        selected_prompt = prompts[0]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out_path = create_session_file(
        session_dir=SESSIONS_DIR,
        prompt_type=args.type.lower(),
        prompt_data=selected_prompt,
        now_str=now_str,
    )

    print(f"Created new practice session:")
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
    """Handle 'stats' subcommand: summary of weaknesses and completed sessions."""
    print("=======================================================")
    print(" TOEFL Agent Studio Progress & Weakness Summary")
    print("=======================================================")

    # Weakness Log Stats
    if WEAKNESS_LOG_PATH.exists():
        try:
            log_data = json.loads(WEAKNESS_LOG_PATH.read_text(encoding="utf-8"))
            missed = log_data.get("missed_vocab", [])
            upgrades = log_data.get("expression_upgrades", [])
            print(f"\n[Weakness Log]")
            print(f"- Total Missed Words Tracked: {len(missed)}")
            print(f"- Total Expression Upgrades:  {len(upgrades)}")

            if missed:
                sorted_missed = sorted(
                    missed, key=lambda x: x.get("error_count", 0), reverse=True
                )
                print("\n  Top Missed Words:")
                for item in sorted_missed[:5]:
                    w = item.get("word", "")
                    cnt = item.get("error_count", 0)
                    m = item.get("meaning_ko", "")
                    last = item.get("last_missed", "")
                    print(f"  * {w:<15} (Errors: {cnt}) - {m} [Last: {last}]")
        except Exception as e:
            print(f"\n[Weakness Log]: Error reading log: {e}")
    else:
        print("\n[Weakness Log]: No weakness log found yet (data/my_weakness_log.json).")

    # Session Stats
    if SESSIONS_DIR.exists():
        session_files = [
            f for f in SESSIONS_DIR.glob("*.md") if f.name != ".gitkeep"
        ]
        print(f"\n[Practice Sessions]")
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

    # Subcommand: ctest
    parser_ctest = subparsers.add_parser(
        "ctest", help="Run Complete the Words vocabulary drills"
    )
    parser_ctest.add_argument("--day", type=int, help="Vocabulary day (1-4)")
    parser_ctest.add_argument(
        "--count", type=int, default=5, help="Number of drill items (default: 5)"
    )
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
        "stats", help="Display weakness log and session statistics"
    )

    return parser


def main() -> None:
    _configure_io_encoding()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ctest":
        cmd_ctest(args)
    elif args.command == "new-session":
        cmd_new_session(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
