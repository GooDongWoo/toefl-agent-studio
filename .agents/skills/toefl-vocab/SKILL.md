---
name: toefl-vocab
description: Use when the user triggers $toefl-vocab or requests a 2026 Revised TOEFL iBT daily vocabulary drill, Complete the Words practice, academic synonym matching, or collocation sentence coaching.
---

# TOEFL Vocab Mastery Skill (`toefl-vocab`)

## Purpose
Administer a structured daily **20 fresh words (+ up to 5 active review words = 20+N items)** drill tailored for the **2026 Revised TOEFL iBT** across three strictly separated sequential phases (`Phase 1: Complete the Words` $\rightarrow$ `Phase 2: Academic Synonym Match` $\rightarrow$ `Phase 3: Collocation Production`) in a stealth IDE workflow.

---

## Repository Resolution & Context Guardrail

1. **Repo Root Resolution**:
   - Check if `data/vocab_seed.json` and `scripts/drill.py` exist in the current working directory (`./`). If so, run commands from `./` (preserving work-PC `git clone` portability).
   - Otherwise (when invoked globally from another workspace on the home PC), use `~/toefl-agent-studio` (`C:\Users\dongwoo\toefl-agent-studio`) as the working directory: `cd` into it first or invoke `python C:\Users\dongwoo\toefl-agent-studio\scripts\drill.py ...` so relative `scripts/drill.py` lookups never fail.
2. **CRITICAL — Never Open `data/vocab_seed.json` Directly**:
   - `data/vocab_seed.json` holds **6,000+ words (300+ days)**. NEVER call `read_file` on it or dump the full JSON file.
   - Always fetch today's slice via CLI:
     ```bash
     python scripts/drill.py today --json
     ```
     (Supports optional `--day N` and `--section core|band5|band6` when the user specifies a day or tier.)

---

## Strict Phase Isolation & Anti-Spoiler `<HARD-GATE>`

1. **One Phase Per Turn (No Multi-Phase Dumping)**:
   - Turn 1: Output **ONLY Phase 1** (`Complete the Words`) and **STOP**.
   - Turn 2 (after Phase 1 answers): Grade Phase 1 + show every word's meaning & examples, then immediately below output **ONLY Phase 2** (`Academic Synonym Match`) and **STOP**.
   - Turn 3 (after Phase 2 answers): Grade Phase 2 + nuance coaching, then immediately below output **ONLY Phase 3** (`Collocation Production`) and **STOP**.
   - Turn 4 (after Phase 3 sentences): Grade Phase 3, sync `data/my_weakness_log.json`, and present the final summary.
2. **Zero Answer Leak**: NEVER display the unmasked word list, Phase 2 options, or Phase 3 prompts during Phase 1.
3. **Zero Synonym Spoiler**: During Phase 1 feedback, NEVER print `synonyms` or `collocations`—reveal them only after Phase 2 is graded.
4. **Missing Review Metadata Fallback**: If an item in `review_items` was logged outside `vocab_seed.json` and has empty `example` / `masked_example` / `synonyms`, dynamically create a 2026 TOEFL academic sentence masked by the 2026 rule (first **2** chars for `len <= 5`, first **3** chars for `len >= 6`), plus natural synonyms and collocations.

---

## 3-Phase Sequential Workflow (20+N Words)

### Step 1: Load Today's Bundle (`20 + N` Items)
Run `python scripts/drill.py today --json` to retrieve:
- `day` and `max_day`
- `fresh_items` (20 words across `core`, `band5`, `band6`)
- `review_items` (up to `N <= 5` unmastered words from `data/my_weakness_log.json`, sorted by `error_count`)

Announce today's scope concisely (e.g., `Day X / 300 — 신규 20단어 (Core · Band 5.0 · Band 6.0) + 오답 복습 N단어`) and proceed immediately to **Phase 1 ONLY**.

### Step 2: Phase 1 — Complete the Words (`20 + N` Items)
Present **all `20 + N` items** numbered sequentially `1` to `20+N`, organized visibly under tier subheadings (`### Core`, `### Band 5.0`, `### Band 6.0`, plus `### Active Review` if `review_items` is non-empty):
- Use `masked_example` with `[pos]` (and `[REVIEW]` badge for review items).
- Format:
  ```markdown
  ### 📝 Phase 1: Complete the Words (1 ~ 20+N)
  #### Core
  1. [adj] The professor assigned a com__________ review of modern geopolitical conflicts.
  ...
  #### Band 5.0
  8. [v] Engineers introduced flood barriers to mit_____ the damage caused by seasonal typhoons.
  ...
  #### Band 6.0
  15. [v] The university provost attempted to ass____ student concerns regarding tuition hikes.
  ...
  #### Active Review (if any)
  21. [v] [REVIEW] ...
  ```
- **STOP** and wait for the user's Phase 1 answers.

### Step 3: Phase 1 Feedback (Every Word) + Phase 2 Presentation
When the user submits Phase 1 answers, respond with **Part A** followed immediately by **Part B**:

#### Part A — Phase 1 Grading & Full Per-Word Review (All `20 + N` Words)
1. **정오답 채점 요약**: Report the Phase 1 score (`X / (20+N)`), clearly listing which items were correct (`O`) and which were missed (`X`: `사용자 답안 -> 정답`, with a brief Korean explanation of spelling/prefix/root).
2. **전 단어 뜻 · 원문 복원 · 추가 예문 2개 (정답/오답 구분 없이 20+N개 전체 필수 출력)**:
   For **every single word** (`1` to `20+N`), display concisely:
   - `N. **word** [pos | tier] (✅ / ❌) — <meaning_ko>`
   - `원문: <Phase 1 example with full target word bolded> — <한국어 해석>`
   - `예문 1: <new 2026 TOEFL academic/workplace sentence> — <한국어 해석>`
   - `예문 2: <second distinct example sentence> — <한국어 해석>`
   *(Anti-spoiler: do NOT show `synonyms` or `collocations` in Part A.)*

#### Part B — Phase 2: Academic Synonym Match (4–5 Mini-Groups)
Immediately below Part A, group all `20 + N` words into **4–5 mini-groups of ~5 words** (e.g., 4 groups of 5 for 20 words, or 4–5 groups of 4–6 words when review items are included) so matching stays fast and readable:
```markdown
### 🔗 Phase 2: Academic Synonym Match
각 그룹의 단어에 가장 가까운 동의어 묶음을 연결하세요 (예: `G1: 1-b, 2-d, ...`).

#### Group 1 (1–5)
- **Words**: 1. `comprehensive` | 2. `constitute` | 3. `correlation` | 4. `differentiate` | 5. `imply`
- **Options**: a. `[comprise / form]` | b. `[exhaustive / thorough]` | c. `[insinuate / suggest]` | d. `[association / link]` | e. `[distinguish / separate]`
```
- **STOP** and wait for the user's Phase 2 answers.

### Step 4: Phase 2 Feedback + Phase 3 Presentation
When the user submits Phase 2 answers, respond with **Part A** followed immediately by **Part B**:

#### Part A — Phase 2 Grading & Synonym/Nuance Coaching
- Report Phase 2 score (`X / (20+N)`), identify every correct and missed match (`#N: 선택 -> 정답`), and explain nuanced differences in Korean (especially for confusable pairs such as `mitigate` vs `assuage`).
- Now reveal the full `synonyms` and key `collocations` for missed or high-value items.

#### Part B — Phase 3: Collocation Production (2–3 Sentences)
- Select **2–3 high-impact collocations** from today's `band5` / `band6` words (prioritizing words missed in Phase 1 or Phase 2; if 100% accurate, choose top academic `band5`/`band6` collocations).
- Ask the user to write **2–3 original academic sentences** using those collocations.
- **STOP** and wait for the user's sentences.

### Step 5: Phase 3 Evaluation & Mandatory State Sync
When the user submits their Phase 3 sentences:
1. **Evaluate per `AGENTS.md` Section 4**:
   - Provide sentence-by-sentence `diff` corrections, **Band 5.5+ Native Upgrades**, and concise **Korean pedagogical coaching** (grammar, preposition, register, Konglish fixes).
2. **Track Deduplicated Outcomes**:
   - `missed_words`: deduplicated union of words missed in Phase 1 **or** Phase 2.
   - `passed_review_words`: review words answered accurately in **both** Phase 1 and Phase 2.
3. **Run Deterministic State Sync**:
   ```bash
   python scripts/drill.py record-vocab --missed <word1> ... --passed <rev1> ... --complete-day <day>
   ```
   *(Omit `--missed` or `--passed` if empty; omit `--complete-day` when filtering by `--section` without finishing the day. If the user ends the session early after Phase 1 or Phase 2, still run `record-vocab` for already-graded words without `--complete-day`.)*
4. **Sync `expression_upgrades`**:
   If any Phase 3 sentence had Konglish or awkward phrasing, append an entry to `expression_upgrades` in `data/my_weakness_log.json` using this exact schema:
   ```json
   {
     "date": "YYYY-MM-DD",
     "task_type": "vocab_collocation",
     "my_draft": "<user draft>",
     "native_upgrade": "<native upgrade>",
     "key_takeaway": "<concise takeaway in Korean/English>"
   }
   ```
5. **Final Summary**:
   - Score breakdown (`Phase 1 CTEST`, `Phase 2 Synonyms`, `Phase 3 Writing highlights`)
   - Newly logged missed words vs graduated (`mastered`) words
   - Updated progress (`Day D / 300`) and CLI reminder: `python scripts/drill.py stats`
