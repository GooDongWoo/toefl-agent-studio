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
