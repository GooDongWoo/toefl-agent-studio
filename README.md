# 🎯 TOEFL Agent Studio (`toefl-agent-studio`)

> **Stealth AI-Powered 2026 Revised TOEFL iBT Studio for Work PCs**
> Target: **Band 5.0+ / 100+ (Section 25+)** for Georgia Tech OMSCS Admission.
> Zero External Dependencies | Pure Python Stdlib | Local Markdown & Agent Skills

---

## 🌟 Overview & Design Philosophy

`toefl-agent-studio` is a self-contained training studio designed for practicing the **2026 Revised TOEFL iBT** directly inside a modern IDE (VS Code or Antigravity) on a corporate work PC without drawing unnecessary attention or violating enterprise security policies.

### Core Architectural Principles
1. **Zero External Dependencies**: Built 100% on the Python 3.10+ standard library (`json`, `argparse`, `pathlib`, `re`, `datetime`, `random`, `unittest`). No `pip install`, virtual environment, or external wheels required.
2. **One-Way Deployment**: Clone and pull from GitHub (`https://github.com/GooDongWoo/toefl-agent-studio.git`) on your work PC. Runtime training logs (`sessions/*.md`, `data/my_weakness_log.json`) are strictly `.gitignore`d, ensuring zero personal data leaks.
3. **Stealth Office Workflows**:
   - **Writing**: Conducted in clean, standard Markdown worksheets (`sessions/YYYY-MM-DD_session.md`).
   - **Speaking (`Take an Interview`)**: Practiced silently via **Speed-Typing** (45–60 seconds per response) to hone English sentence formulation reflexes without speaking aloud.
   - **Vocabulary**: 2026-format `Complete the Words` spelling masks and collocations.
4. **Agent Constitution & Skills**: Governed by `AGENTS.md` and 3 specialized skills in `.agents/skills/` (`$toefl-vocab`, `$toefl-speaking`, `$toefl-writing`).

---

## 🚀 1-Minute Quick Start (Company PC)

### 1. Clone the Repository
```bash
git clone https://github.com/GooDongWoo/toefl-agent-studio.git
cd toefl-agent-studio
```

### 2. Verify System Integrity
Run the built-in unit test suite (7 tests, zero dependencies):
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

---

## 📅 Recommended 30-Minute Daily Office Routine

| Time Window | Duration | Drill Type | Method / Tool |
| :--- | :---: | :--- | :--- |
| **09:00 – 09:05** | 5 min | **Morning Vocab Warmup** | Trigger `$toefl-vocab` or run `python scripts/drill.py ctest --count 5`. |
| **12:40 – 12:55** | 15 min | **Silent Speaking Interview** | Trigger `$toefl-speaking` for 4 sequential speed-typing questions (0s prep). |
| **17:30 – 17:45** | 15 min | **Afternoon Writing Drill** | Run `python scripts/drill.py new-session --type email` (7 min) or `--type discussion` (10 min), draft, check with `scripts/drill.py check`, and request AI feedback via `$toefl-writing`. |

---

## 🛠️ CLI Trainer Reference (`scripts/drill.py`)

All commands use only the Python standard library:

### 1. Complete the Words Vocabulary Quiz (`ctest`)
Generates 2026 iBT in-context spelling fill-ins (prioritizing previously missed words from `data/my_weakness_log.json`):
```bash
python scripts/drill.py ctest --count 5
# Or specify a target day:
python scripts/drill.py ctest --day 1 --count 5
```

### 2. Create a Timed Writing Worksheet (`new-session`)
Generates a timestamped practice file in `sessions/`:
```bash
# Task 1: Write an Email (7 minutes, 80-140 words, 3 bullets)
python scripts/drill.py new-session --type email

# Task 2: Academic Discussion (10 minutes, 100+ words)
python scripts/drill.py new-session --type discussion

# Speaking: Take an Interview worksheet
python scripts/drill.py new-session --type interview
```

### 3. Verify Word Count and Timing (`check`)
Inspects your response under `## ✍️ My Response` and records stats to the file metadata:
```bash
python scripts/drill.py check --file sessions/YYYY-MM-DD_email_email_01.md
```

### 4. View Cumulative Weakness Statistics (`stats`)
Summarizes completed sessions, top 10 missed vocabulary words, and recent native expression upgrades:
```bash
python scripts/drill.py stats
```

---

## 🤖 Dedicated Agent Coaching Skills

When interacting with Antigravity / Claude / Gemini inside your IDE:

- **`$toefl-vocab`**: Conducts 3-phase warmup (`Complete the Words` $\rightarrow$ Synonym Match $\rightarrow$ 1-Sentence Collocation).
- **`$toefl-speaking`**: Acts as the dynamic 2026 interviewer, presenting **one question at a time** (Q1 $\rightarrow$ Q2 $\rightarrow$ Q3 $\rightarrow$ Q4), grading on Band 1.0–6.0, generating a side-by-side comparison table, and logging top 3 upgrades.
- **`$toefl-writing`**: Audits 3 prompt bullet points, calculates word count, provides `diff`-block corrections, crafts a Band 5.5+ model rewrite preserving your ideas, and logs upgrades to `data/my_weakness_log.json`.

---

## 📊 2026 TOEFL iBT Band Scale & Score Conversion

| Band | Section Score (0–30) | Total Equivalent (0–120) | Proficiency Level & Target |
| :---: | :---: | :---: | :--- |
| **Band 6.0** | 29 – 30 | 116 – 120 | Expert / Native-like precision |
| **Band 5.5** | 27 – 28 | 108 – 115 | Advanced High |
| **Band 5.0** | **24 – 26** | **96 – 107** | **Target: Georgia Tech OMSCS (100+)** |
| **Band 4.5** | 21 – 23 | 84 – 95 | Intermediate High |
| **Band 4.0** | 18 – 20 | 72 – 83 | Intermediate |
| **Band 3.0** | 12 – 17 | 48 – 71 | Modest |
| **Band 1.0–2.0**| 0 – 11 | 0 – 47 | Extremely Limited |

---

## 📁 Repository Directory Structure

```text
toefl-agent-studio/
├── AGENTS.md                        # AI coach constitution & grading rubrics
├── README.md                        # Quick start & daily office routine guide
├── .gitignore                       # Excludes sessions/ and local weakness logs
├── .agents/
│   └── skills/
│       ├── toefl-vocab/SKILL.md     # 5-min vocab warmup & spelling drill
│       ├── toefl-speaking/SKILL.md  # 4-question speed-typing interview
│       └── toefl-writing/SKILL.md   # Email & Academic Discussion coach
├── data/
│   ├── vocab_seed.json              # Curated TOEFL academic vocabulary DB
│   ├── prompt_bank.json             # 2026 Revised writing & speaking prompts
│   └── my_weakness_log.json         # (Runtime) Auto-accumulated errors & upgrades
├── sessions/
│   └── .gitkeep                     # Local practice worksheets (git-ignored)
├── scripts/
│   └── drill.py                     # Zero-dependency CLI trainer
└── tests/
    ├── test_seed_data.py            # Validates JSON database schema
    ├── test_drill.py                # Tests CLI helper functions
    └── test_skills_integrity.py     # Verifies skills frontmatter & integrity
```
