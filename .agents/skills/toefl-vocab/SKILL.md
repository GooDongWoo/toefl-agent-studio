---
name: toefl-vocab
description: 2026 Revised TOEFL iBT 5-minute morning vocabulary warmup combining Complete the Words (in-context spelling mask), synonym matching, and 1-sentence collocation drills with spaced repetition from my_weakness_log.json.
---

# TOEFL Vocab Mastery Skill (`toefl-vocab`)

## Purpose
This skill conducts a rapid 5-to-10-minute morning warmup in a stealth IDE terminal environment. It is tailored for the **2026 Revised TOEFL iBT** vocabulary format (`Complete the Words`) and leverages spaced repetition to convert passive vocabulary into active writing and speaking assets.

---

## Data Sources
- Seed Database: `data/vocab_seed.json` (Curated high-frequency academic vocabulary with collocations and context sentences)
- Weakness Tracker: `data/my_weakness_log.json` (Cumulative log of user errors and expression upgrades)
- Helper CLI: `python scripts/drill.py ctest`

---

## 3-Phase Warmup Workflow

When the user triggers `$toefl-vocab` or asks for a vocabulary drill, execute the following three phases:

### Step 1: Candidate Selection (Weakness-First)
1. Read `data/my_weakness_log.json`. Check `missed_vocab` for words with `error_count >= 1`.
2. If available, prioritize 2–3 previously missed words.
3. Supplement with 2–3 fresh words from `data/vocab_seed.json` (by Day or random selection) for a total of 5 drill items.

### Step 2: Phase 1 — Complete the Words (2026 iBT Spelling in Context)
Present context sentences where the target word is partially masked according to the 2026 exam rule:
- Words with 5 or fewer characters: show first **2** characters (e.g., `imply` $\rightarrow$ `im___`).
- Words with 6 or more characters: show first **3** characters (e.g., `ambiguous` $\rightarrow$ `amb______`, `mitigate` $\rightarrow$ `mit_____`).

**Format:**
```markdown
### 📝 Phase 1: Complete the Words
Fill in the blanks with the correct full word:

1. [adj] The laboratory results were amb______ and could not confirm the hypothesis.
2. [v] The company introduced new safety protocols to mit_____ potential liability risks.
3. [v] The author seems to im___ that the current economic theory is outdated.
```

Wait for the user's answers or grade them inline.

### Step 3: Phase 2 — Academic Synonym Match
Test active recall of academic synonyms required for paraphrasing in Writing and Speaking:
```markdown
### 🔗 Phase 2: Academic Synonym Match
Match each target word to its closest academic synonyms:
- Words: `ambiguous`, `mitigate`, `viable`
- Options: [alleviate / lessen], [feasible / workable], [vague / equivocal]
```

### Step 4: Phase 3 — Collocation 1-Sentence Production
Ask the user to write 1 original, grammatically sound academic sentence using a high-frequency collocation from `data/vocab_seed.json`:
- e.g., *"Write one sentence using either `mitigate risk` or `viable alternative`."*

---

## Evaluation & Weakness Logging Protocol

When reviewing the user's responses:

1. **Check Accuracy**:
   - Verify exact spelling in Phase 1.
   - Verify semantic alignment in Phase 2.
   - Verify syntax, preposition use, and natural academic register in Phase 3.
2. **Pedagogical Feedback**:
   - Provide concise Korean explanations for any error or awkward phrasing.
   - Highlight natural native collocations.
3. **Mandatory Automatic Log Update**:
   - For every missed word in Phase 1 or 2, record or increment `error_count` in `data/my_weakness_log.json` under `missed_vocab`.
   - If the sentence in Phase 3 used an unnatural Konglish pattern, add the correction to `expression_upgrades` in `data/my_weakness_log.json`.
4. **Summary & CLI Tip**:
   - Conclude with a quick summary score (e.g., `5/5 Perfect!` or `4/5 (1 word added to weakness log)`).
   - Remind the user they can also run standalone drills anytime via:
     ```bash
     python scripts/drill.py ctest --count 5
     python scripts/drill.py stats
     ```
