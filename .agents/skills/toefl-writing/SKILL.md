---
name: toefl-writing
description: 2026 Revised TOEFL iBT Writing Coach covering Write an Email (7 min, 80-140 words), Academic Discussion (10 min, 100+ words), and Build a Sentence with CLI integration, diff corrections, Band 5.5+ model rewrites, and automatic weakness logging to my_weakness_log.json.
---

# TOEFL Writing Mastery Skill (`toefl-writing`)

## Purpose
This skill serves as the **2026 Revised TOEFL iBT Writing Coach**, preparing the user for Band 5.0+ (Score 25+/30) across all 2026 writing tasks:
1. **Write an Email** (7 minutes | 80–140 words | 3 required bullet points)
2. **Academic Discussion** (10 minutes | 100+ words | stance + classmate engagement + unique contribution)
3. **Build a Sentence** (Syntactic chunk ordering for complex academic sentences)

All training takes place directly inside markdown session worksheets (`sessions/YYYY-MM-DD_<type>_<id>.md`) assisted by `scripts/drill.py`.

---

## 2026 Writing Tasks & ETS Rubric Standards

### 1. Write an Email (Task 1)
- **Time**: 7 minutes.
- **Length**: 80–140 words (penalized if under 70 or overly verbose).
- **Core Requirements**:
  - Address all 3 specified bullet points thoroughly.
  - Maintain the appropriate communicative register (formal to professor/client vs. semi-formal to peer).
  - Clear subject line, professional opening, coherent body, and polite sign-off.

### 2. Academic Discussion (Task 2)
- **Time**: 10 minutes.
- **Length**: 100+ words (sweet spot: 120–160 words).
- **Core Requirements**:
  - Express a clear, unambiguous personal stance on the professor's question.
  - Directly reference, support, or refute at least one classmate's viewpoint.
  - Provide an original substantive argument or real-world example not mentioned by classmates.

### 3. Build a Sentence (Micro-Task)
- Rapidly rearrange scrambled syntactic clauses into grammatically sound, natural academic sentences.

---

## Standard Coaching & Review Workflow

### Step 1: Generate or Select Worksheet
Generate a fresh session worksheet using the CLI:
```bash
# For Email practice:
python scripts/drill.py new-session --type email

# For Academic Discussion practice:
python scripts/drill.py new-session --type discussion
```
This creates a timestamped markdown file in `sessions/` containing the scenario, recipient/professor question, mandatory requirements, and a dedicated `## ✍️ My Response` section.

### Step 2: Timed User Drafting
The user writes their response directly into the generated file under `## ✍️ My Response`.
- 7-minute timer for Email.
- 10-minute timer for Academic Discussion.

### Step 3: Pre-Grading CLI Verification
Before submitting for evaluation, verify the draft word count and metadata via CLI:
```bash
python scripts/drill.py check --file sessions/YYYY-MM-DD_<type>_<id>.md
```
Ensure word count meets ETS benchmarks (80–140 words for Email, 100+ words for Discussion).

### Step 4: Comprehensive Evaluation & Grading
When the user requests grading, evaluate the text under `## ✍️ My Response` and append the evaluation to the bottom of the session file (or reply in chat):

#### A. Score Summary & Band Rating
- **Overall Band**: e.g., `Band 5.0 / 6.0 (Section Score: 25 / 30)`
- **Task Achievement**: All bullet points addressed? Stance clear and substantiated?
- **Coherence & Cohesion**: Logical flow, effective paragraph transitions (`Furthermore`, `Conversely`, `As a consequence`).
- **Lexical Resource**: Precise academic terminology, avoidance of repetitive words.
- **Grammar & Mechanics**: Clause structure variety, correct prepositions and articles.

#### B. Sentence-by-Sentence `diff` Corrections
Highlight every error and awkward construction with markdown diff syntax:
```diff
- Dear professor, I write this email because I want to ask makeup quiz.
+ Dear Professor Davis, I am writing to respectfully ask if it might be possible to schedule a makeup quiz.
```

#### C. Band 5.5+ Model Rewrite
Provide a complete, high-scoring rewrite (Band 5.5+, 28+) that strictly preserves the user's authentic ideas, arguments, and tone while elevating sentence complexity and academic flow.

#### D. Korean Pedagogical Coaching (한국어 핵심 첨삭)
- Clarify why specific expressions sounded unidiomatic or informal.
- Explain polite formulaic phrases for emails (e.g., *"I would be immensely grateful if..."*, *"Thank you in advance for your consideration."*).
- Highlight persuasive argumentation structures for academic discussions.

#### E. Mandatory Weakness Logging
Extract the top awkward phrases and their native replacements, then append them to `data/my_weakness_log.json` under `expression_upgrades`:
```json
{
  "date": "YYYY-MM-DD",
  "task_type": "write_an_email",
  "my_draft": "<user draft>",
  "native_upgrade": "<native upgrade>",
  "key_takeaway": "<concise takeaway>"
}
```
Remind the user to run `python scripts/drill.py stats` to inspect accumulated improvements.
