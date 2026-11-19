# TOEFL Agent Studio 어휘 6,000+ 확장 및 일일 20단어 섹션 학습 설계 스펙

- **작성일**: 2026-11-20
- **대상 저장소**: `C:\Users\dongwoo\toefl-agent-studio` (및 전역 스킬 연동 `C:\Users\dongwoo\.agents`, Obsidian 스펙 문서)
- **목표**: [vocab_seed.json](../../../data/vocab_seed.json)의 어휘 규모를 24단어에서 **6,000단어(300일 분량)**로 확장하고, `Core` / `Band 5.0` / `Band 6.0` 3개 티어 섹션 기반의 **일일 20단어(+복습 최대 5단어) 미니배치 학습 체계**로 개편한다.

---

## 1. 핵심 설계 결정 (Design Decisions)

| 항목 | 확정 설계 |
| :--- | :--- |
| **섹션 분류 축** | 빈출도·난이도 티어 3종 (`core`, `band5`, `band6`) |
| **목표 단어 총량** | **6,000단어** (`300일 × 일 20단어`, 티어당 각 2,000단어) — 추후 60단어 배수 단위로 확장 가능한 구조 |
| **커리큘럼 편성** | **매일 티어 혼합형 (Day 1~300)** — 하루 20단어 내에 3티어를 `6~7 : 6~7 : 6~7` 균등 로테이션 배치 |
| **오답 복습 정책** | **오늘의 신규 Day 20개 고정 + 활성 오답 복습 최대 5개 추가** (하루 총 20~25문항) |
| **복습 졸업 기준** | 복습 퀴즈에서 **연속 2회 정답** 시 `mastered: true`로 졸업 (`error_count` 이력은 보존, 재오답 시 초기화) |
| **스킬 진행 UX** | **섹션별 3라운드 미니배치** (`Core` → `Band 5.0` → `Band 6.0` + 복습 순으로 6~8문항씩 CTEST·동의어 즉시 피드백) 후 핵심 콜로케이션 2~3문장 작문 |
| **CLI 및 상태 추적** | Python 표준 라이브러리 기반 `scripts/drill.py` 확장 (`today`, `record-vocab`, `ctest`, `stats`) + `my_weakness_log.json`에 `vocab_progress` 저장 |
| **컨텍스트 가드레일** | 6,000단어(~2.8 MB) `vocab_seed.json` 직접 읽기 금지 → `drill.py today --json`으로 오늘 분량(20~25개, ~4 KB)만 조회 |
| **배포·동기화 범위** | `toefl-agent-studio` 개편 + 홈 PC 전역(`~/.agents/skills`) 토플 3종 스킬 정션 연결 + Obsidian 스펙/대시보드 업데이트 |

---

## 2. 아키텍처 및 데이터 계층 (`data/`)

### 2.1 단일 `vocab_seed.json` + CLI JSON 슬라이싱 채택 이유
- 매일 3개 티어를 혼합 출제하므로 티어별 분할 JSON(Approach B)은 결국 매번 3개 파일을 모두 읽어야 하여 이점이 없다.
- 6,000건 JSON은 Python `json.loads()` 기준 수십 ms 내에 파싱되므로 SQLite(Approach C) 없이도 빠르며, Git diff 리뷰와 사내 PC 무의존성(`git clone` / `git pull`) 및 기존 테스트(`test_seed_data.py`) 호환성을 100% 유지한다.
- 단, AI 에이전트가 대용량 JSON을 통째로 컨텍스트에 올리지 않도록 `toefl-vocab/SKILL.md`에서 `vocab_seed.json` 직접 열람을 금지하고 `drill.py today --json` 호출을 강제한다.

### 2.2 `data/vocab_seed.json` 스키마
기존 8개 필수 필드를 유지하고 `section` 필드를 추가한다.

```json
{
  "id": "day001_001",
  "day": 1,
  "section": "core",
  "word": "comprehensive",
  "pos": "adjective",
  "meaning_ko": "포괄적인, 종합적인",
  "synonyms": ["exhaustive", "thorough", "extensive"],
  "example": "The professor assigned a comprehensive review of modern geopolitical conflicts.",
  "collocations": ["comprehensive study", "comprehensive review", "comprehensive guide"]
}
```

- **불변 조건 (Invariants)**:
  1. 총 단어 수는 `6,000`개 이상이며 `60`의 배수를 유지한다(1차 구축 목표: 정확히 **6,000개 = 300일**, 각 섹션 `core`, `band5`, `band6` 동일하게 `총량 / 3 = 2,000개`씩).
  2. `day`는 `1..N` (`N = 총량 / 20`, 6,000개 기준 `1..300`), 모든 Day마다 정확히 20개 항목 배치.
  3. 3일 주기 균등 로테이션:
     - `day % 3 == 1`: `core` 7 + `band5` 7 + `band6` 6 = 20
     - `day % 3 == 2`: `core` 7 + `band5` 6 + `band6` 7 = 20
     - `day % 3 == 0`: `core` 6 + `band5` 7 + `band6` 7 = 20
  4. `word.strip().lower()` 기준 전체 6,000개 내 중복 0건.
  5. 기존 24개 시드 단어를 모두 보존하고 적절한 `section`을 부여하여 `Day 1~2`에 배치.
  6. 모든 항목은 `re.search(rf"\b{re.escape(word)}\b", example, re.IGNORECASE)`가 매칭되어 `mask_word_in_sentence(example, word) != example`을 보장.
  7. `synonyms` 2개 이상(권장 3개, 표제어와 중복 불가), `collocations` 2개 이상(권장 3개), `meaning_ko` 비어 있지 않음.

### 2.3 6,000+ 어휘 구축 파이프라인 (Build-Time Only)
런타임은 Python 표준 라이브러리 100% 무의존성을 유지하고, 집 PC에서의 시드 구축만 3단계 파이프라인으로 수행한다:
1. **1단계 — 마스터 단어 풀 선별**: 공개 학술·어휘 코퍼스(NGSL · NAWL · AWL · CEFR B1~C2 · TOEFL 빈출 어휘) 기반으로 중복·단순 굴절형(복수형/과거형 중복)을 제거한 6,000개 표제어를 `core`(B1~B2 학술 기본), `band5`(B2~C1 TOEFL 핵심), `band6`(C1~C2 고득점·고난도) 2,000개씩으로 분류하고 Day 1~300 로테이션 슬롯을 배정한다.
2. **2단계 — 병렬 배치 생성 (`run_workflow`)**: 슬롯이 배정된 6,000개 단어를 병렬 에이전트 배치로 처리해 `pos`, `meaning_ko`, `synonyms`, `example`, `collocations`를 생성한다.
3. **3단계 — 전수 검증 및 병합**: 검증 스크립트로 스키마·중복·CTEST 정규식·티어/Day 분포를 전수 검증하고 실패 항목만 재생성한 뒤 `data/vocab_seed.json`으로 병합·확정한다.

### 2.4 `data/my_weakness_log.json` 확장 스키마
기존 `missed_vocab`, `expression_upgrades`를 그대로 유지하면서 `vocab_progress`와 복습 졸업 필드를 하위 호환 방식으로 추가한다.

```json
{
  "missed_vocab": [
    {
      "word": "assuage",
      "meaning_ko": "완화하다, 달래다",
      "section": "band6",
      "error_count": 2,
      "last_missed": "2026-11-20",
      "streak": 0,
      "mastered": false
    }
  ],
  "expression_upgrades": [],
  "vocab_progress": {
    "current_day": 1,
    "completed_days": [],
    "last_studied": null
  }
}
```

- **하위 호환 규칙**: 기존 파일에 `vocab_progress`, `streak`, `mastered`, `section`이 누락돼 있어도 로더가 기본값(`current_day=1`, `completed_days=[]`, `last_studied=None`, `streak=0`, `mastered=false`)으로 안전하게 보정한다.
- **복습 상태 전이**:
  - 오답 기록(`record_missed_vocab`): `error_count += 1`, `last_missed = today`, `streak = 0`, `mastered = False`. (이미 `mastered`였던 단어도 다시 틀리면 활성 복습으로 복귀.)
  - 복습 정답 기록(`record_correct_vocab`): 활성(`not mastered`) 항목에 대해 `streak += 1`; `streak >= 2`가 되면 `mastered = True`로 졸업 처리.
  - Day 완료 기록(`mark_day_completed`): `day`를 `completed_days`에 추가(오름차순 중복 제거)하고, `current_day`를 `1..max_day` 중 아직 완료하지 않은 가장 작은 Day로 갱신(모두 완료 시 `max_day`).

---

## 3. CLI 설계 (`scripts/drill.py`)

모든 기능은 Python 3.10+ 표준 라이브러리만 사용한다.

### 3.1 핵심 순수/상태 함수
- 기존 유지: `mask_word_in_sentence`, `count_response_words`, `record_missed_vocab`(선택 인자 `section=""` 추가 및 `streak=0`, `mastered=False` 리셋 포함하되 기존 4인자 시그니처 호환 유지), `create_session_file`.
- 신규 추가:
  - `load_weakness_log(log_path: Path) -> Dict[str, Any]` / `save_weakness_log(log_path: Path, data: Dict[str, Any]) -> None`
  - `record_correct_vocab(log_path: Path, word: str) -> Dict[str, Any]`
  - `mark_day_completed(log_path: Path, day: int, max_day: int, today_iso: str) -> Dict[str, Any]`
  - `select_daily_vocab(vocab_items, log_data, day=None, section=None, count=20, max_review=5, include_review=True)`:
    - **일반 일일 모드 (`section=None`)**: `target_day`(지정 `--day` 또는 `vocab_progress.current_day`)에서 최대 `count`개(기본 20) 신규 단어를 `core -> band5 -> band6` 순서로 추출하고, `include_review=True`이면 활성(`not mastered`) `missed_vocab` 중 오늘 신규 단어와 겹치지 않는 최대 `max_review`개(기본 5)를 `error_count` 내림차순으로 선별해 `vocab_seed.json` 메타데이터(예문·동의어·섹션)와 결합해 반환한다.
    - **섹션 필터 모드 (`section in {"core", "band5", "band6"}`)**: `--day`가 명시되면 해당 Day의 해당 섹션 단어만 반환하고, `--day`가 생략되면 `current_day` 이상 구간에서 해당 섹션 단어 `count`개를 순차 추출한다.

### 3.2 서브커맨드
1. **`python scripts/drill.py today [--day N] [--section core|band5|band6] [--count 20] [--max-review 5] [--no-review] [--json] [--complete]`**
   - 오늘 학습 대상(신규 20개 + 복습 최대 5개)을 섹션별/복습별로 묶어 출력한다.
   - `--json` 옵션 시 `$toefl-vocab` 스킬이 바로 소비할 수 있는 경량 JSON(`day`, `max_day`, `fresh_items`, `review_items`, `summary`)을 stdout으로 출력한다(각 항목에 `masked_example` 포함).
   - `--complete` 지정 시 해당 Day 완료 상태를 기록한다.
2. **`python scripts/drill.py record-vocab [--missed WORD ...] [--passed WORD ...] [--complete-day N]`**
   - 에이전트가 세션 종료 시 오답 추가/재발(`--missed`), 복습 정답(`--passed`), 일차 완료(`--complete-day`)를 1회 CLI 호출로 원자적(deterministic)으로 반영할 수 있게 한다.
   - `--missed` 단어의 `meaning_ko`와 `section`은 `vocab_seed.json`에서 자동 조회해 채운다(시드에 없는 단어일 경우 빈 문자열 폴백).
3. **`python scripts/drill.py ctest [--day N] [--section core|band5|band6] [--count 20] [--review | --no-review] [--interactive] [--json]`**
   - 기본 `--count`를 `5`에서 `20`으로 상향. `--day` 미지정 + `--section` 미지정 시 `vocab_progress.current_day`를 자동 사용한다.
   - `--review` 단독 지정 시 활성 `missed_vocab`만 집중 복습한다.
   - `--interactive` 모드에서는 `[section]` 및 `[REVIEW]` 배지를 표시하고, 정답 시 `record_correct_vocab`, 오답 시 `record_missed_vocab`을 호출하며, 일반 일일 세션을 끝까지 완료하면 `mark_day_completed`로 진도를 전진시킨다.
4. **`python scripts/drill.py stats`**
   - 기존 출력에 더해 **Vocab Progress (`Day X / 300`, 완료 일수)**, **섹션별 보유/약점 현황**, **활성 복습 vs 졸업(`mastered`) 단어 수**를 표시한다.

---

## 4. 에이전트 스킬 및 전역 연동 설계

### 4.1 `.agents/skills/toefl-vocab/SKILL.md`
- **저장소 경로 해석 (이식성 + 전역 호출 양립)**:
  1. 현재 작업 디렉터리에 `data/vocab_seed.json`과 `scripts/drill.py`가 있으면 상대 경로(`./`) 사용 (사내 PC `git clone` 환경 그대로 유지).
  2. 다른 디렉터리에서 전역 호출된 경우 `C:\Users\dongwoo\toefl-agent-studio` (`~/toefl-agent-studio`)를 저장소 루트로 사용해 실행.
- **대용량 파일 보호 규칙**:
  - `data/vocab_seed.json`을 파일 읽기 도구로 직접 열지 않고, 반드시 `python scripts/drill.py today --json`으로 오늘의 20~25단어만 가져온다.
- **3라운드 섹션 미니배치 진행 프로토콜**:
  1. **데이터 로드**: `today --json` 실행 → 오늘 Day와 신규 20단어(`Core` / `Band 5.0` / `Band 6.0`) + 복습 최대 5단어 확인.
  2. **Round 1 (`Core`, 6~7개 + 관련/미분류 복습)**: `Complete the Words` 빈칸 문항 + 동의어 매칭(보기 셔플) 제시 → 사용자 답안 제출 시 즉시 채점·한국어 해설·정답/오답 추적.
  3. **Round 2 (`Band 5.0`, 6~7개 + 관련 복습)**: 동일 방식 진행 및 즉시 피드백.
  4. **Round 3 (`Band 6.0`, 6~7개 + 관련 복습)**: 동일 방식 진행 및 즉시 피드백.
  5. **Final Round (`Collocation Production`)**: 오늘의 `Band 5.0` / `Band 6.0` 핵심 콜로케이션 2~3개를 선정해 2~3문장 영작 요청 → 문법·어휘 자연스러움 첨삭 및 부자연스러운 표현을 `expression_upgrades`에 기록.
  6. **상태 동기화**: `python scripts/drill.py record-vocab --missed ... --passed ... --complete-day <D>` 실행 후 최종 점수, 새로 오답 등록/졸업된 단어, 누적 `Day D/300` 진도를 요약 보고.

### 4.2 `toefl-speaking` · `toefl-writing` 전역 호출 호환
- [toefl-speaking SKILL.md](../../../.agents/skills/toefl-speaking/SKILL.md) 및 [toefl-writing SKILL.md](../../../.agents/skills/toefl-writing/SKILL.md) 상단에도 동일한 저장소 루트 해석 규칙(CWD 우선, 미존재 시 `~/toefl-agent-studio` 폴백)을 추가해 전역 호출 시 `data/prompt_bank.json`, `data/my_weakness_log.json`, `scripts/drill.py`를 문제없이 찾도록 한다.

### 4.3 홈 PC 전역 정션 연동 (`C:\Users\dongwoo\.agents`)
- `C:\Users\dongwoo\.agents\.gitignore`:
  - `# Project-specific local skills` 아래에 `skills/toefl-vocab`, `skills/toefl-speaking`, `skills/toefl-writing` 추가.
- `C:\Users\dongwoo\.agents\scripts\sync-agent-links.ps1`:
  - 기존 `querying-obsidian-knowledge` 패턴과 동일하게 `~/toefl-agent-studio/.agents/skills/{toefl-vocab,toefl-speaking,toefl-writing}`를 `~/.agents/skills/`에 디렉터리 정션으로 연결한 뒤 `.claude/skills`, `.codex/skills`, `.gemini/skills`까지 전파되도록 스크립트를 확장·실행한다.

---

## 5. 문서·테스트·Obsidian 동기화 범위

1. **저장소 문서 (`toefl-agent-studio`)**:
   - `AGENTS.md`: `$toefl-vocab` 설명(일 20+복습, 3섹션 미니배치, `today --json`) 및 `scripts/drill.py` CLI 예시 갱신.
   - `README.md`: 일일 학습량(20단어+복습), 6,000+ 어휘/300일 구조, `today`/`ctest --section`/`record-vocab`/`stats` 사용법 갱신.
2. **테스트 (`tests/`)**:
   - `tests/test_seed_data.py`: 6,000+ 단어, 60 배수, Day별 20개, 3일 주기 7/7/6 로테이션, `section` 유효성, 중복 0건, `\bword\b` CTEST 마스킹 검증, 기존 24단어 포함 검증.
   - `tests/test_drill.py`: `select_daily_vocab`, `record_correct_vocab`, `record_missed_vocab` 리셋, `mark_day_completed`, 하위 호환 로더, CLI `today --json` / `record-vocab` / `ctest` / `stats` 테스트.
   - `tests/test_skills_integrity.py`: `toefl-vocab` 20단어/섹션/`today --json` 규칙, 3종 스킬의 `my_weakness_log.json` 및 저장소 폴백 규칙 검증.
3. **Obsidian 문서 동기화**:
   - `03_사내PC_토플_에이전트_스튜디오_스펙.md`: 6,000+ 어휘·섹션·CLI 스펙 반영 및 `- [x] 집 PC toefl-agent-studio 일일 단어 학습량 20개+ 설정 업데이트` 완료 처리.
   - `00_토플_마스터_대시보드.md`: 집 PC 동기화 및 6,000+ 어휘 확장 이력 반영.
   - `obsidian_knowledge` MCP `knowledge-index-sync` 실행.
