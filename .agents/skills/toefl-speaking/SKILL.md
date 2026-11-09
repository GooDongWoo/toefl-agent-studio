---
name: toefl-speaking
description: 2026 Revised TOEFL iBT Take an Interview simulation designed for silent office practice using sequential 4-question speed-typing (0 prep, 60s per response), Band 1.0-6.0 rubric scoring, side-by-side native spoken upgrade table, and automatic weakness logging to my_weakness_log.json.
---

# TOEFL Speaking Mastery Skill (`toefl-speaking`)

## Purpose
This skill administers the **2026 Revised TOEFL iBT `Take an Interview`** simulation. Designed specifically for quiet office or workplace environments, it replaces vocal recording with **timed Speed-Typing (45–60 seconds per response)** to build lightning-fast neural reflexes for English sentence synthesis, discourse management, and idiomatic spoken expressions.

---

## The 2026 `Take an Interview` Format
- **Structure**: 4 sequential conversational questions centered on a realistic academic or workplace theme.
- **Preparation Time**: **0 seconds** (instant response required).
- **Response Limit**: 45–60 seconds per question (target 60–100 words typed per question).
- **Question Progression Pattern**:
  1. **Q1 (Personal Fact / Experience)**: Direct recall or current habit.
  2. **Q2 (Specific Elaboration / Detail)**: A concrete incident, challenge, or practical example.
  3. **Q3 (Comparative Analysis)**: Weighing trade-offs, advantages vs. disadvantages, or opposing opinions.
  4. **Q4 (Analytical / Policy Perspective)**: Broad evaluation, future impact, or recommendations.

---

## Sequential 4-Question Interaction Protocol

> [!IMPORTANT]
> **Strict Rule**: NEVER present all four questions at once. A real interview is dynamic and interactive. Present exactly **one question at a time**, waiting for the user's response before delivering the next.

### Step 1: Prompt Selection & Briefing
Select an interview scenario from `data/prompt_bank.json` (`take_an_interview`) or create a dynamic 2026-style scenario.
Output the context briefing and Question 1 only:
```markdown
## 🎙️ 2026 TOEFL Speaking: Take an Interview
**Topic**: Remote Work vs. Office Collaboration
**Format**: 4 sequential questions | 0s prep | 60s speed-typing per response

---
### Question 1 of 4
> *"Do you personally prefer working remotely from home or collaborating in a physical office setting, and why?"*

*(Timer: 60s — Type your response immediately below)*
```

### Step 2: Sequential Progression (Q2 $\rightarrow$ Q3 $\rightarrow$ Q4)
As soon as the user submits their answer to Q1, acknowledge with a natural one-line conversational bridge and immediately ask Question 2. Repeat through Question 4:
- After Q1 response $\rightarrow$ Present Q2 (*"Can you describe a specific project where this preference directly affected your productivity?"*)
- After Q2 response $\rightarrow$ Present Q3 (*"What do you see as the biggest drawback of remote communication compared to in-person discussions?"*)
- After Q3 response $\rightarrow$ Present Q4 (*"Looking ahead, how should technology companies balance organizational culture with employee demands for flexible work?"*)

---

## Evaluation & Feedback Protocol

Once the user completes Question 4, provide a thorough, structured debriefing:

### 1. Score Report (2026 Band Scale & 0–30 Conversion)
- **Overall Band**: e.g., `Band 5.0 / 6.0 (Section Score: 25 / 30)`
- **Core Dimensions**:
  - **Fluency & Delivery**: Word count, pacing, syntactic continuity under time pressure.
  - **Language Use**: Spoken grammatical precision, natural discourse markers, lexical accuracy.
  - **Topic Development**: Direct answers to prompt nuances, logical progression across all 4 questions.

### 2. Side-by-Side Comparison Table
Create a clean side-by-side comparison for all four questions:

| Question | My Draft (Typed Under Pressure) | Native Spoken Upgrade (Band 5.5+) | Key Improvement / Idiomatic Pivot |
| :--- | :--- | :--- | :--- |
| **Q1** | *I prefer remote work because I don't need to waste time in subway and I can focus.* | *"I strongly lean toward remote work, primarily because eliminating the daily commute preserves mental energy for deep, uninterrupted focus."* | `lean toward`, `eliminate commute`, `preserve mental energy` |
| **Q2** | ... | ... | ... |
| **Q3** | ... | ... | ... |
| **Q4** | ... | ... | ... |

### 3. Korean Pedagogical Coaching (한국어 교정 포인트)
- Explain why simple connectors (e.g., repeating *and*, *so*, *because*) weaken speaking scores.
- Teach high-scoring spoken transitions (e.g., *"To be quite frank"*, *"On the flip side"*, *"In the grand scheme of things"*).
- Correct common Korean-English interference errors (e.g., *contact to*, *discuss about*, *makes me hard to*).

### 4. Mandatory Automatic Weakness Logging
Extract the **top 3 most impactful expression upgrades** from the session and append them directly to `data/my_weakness_log.json` under `expression_upgrades`:
```json
{
  "date": "YYYY-MM-DD",
  "task_type": "speaking_interview",
  "my_draft": "<user draft>",
  "native_upgrade": "<native upgrade>",
  "key_takeaway": "<concise takeaway in Korean/English>"
}
```
Remind the user to run `python scripts/drill.py stats` to track cumulative progress.
