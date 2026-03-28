# Memory — 에이전트 기억 시스템

## 왜 Memory가 필수인가?
> LLM은 기본적으로 **아무것도 기억하지 못한다.**  
> 매 요청이 "처음 만나는 대화"처럼 처리된다.  
> Memory 시스템이 없으면 하네스 설계 이력, 부품 이력, 대화 맥락이 모두 사라진다.

---

## Memory 구조 전체 그림

```
┌──────────────────────────────────────────────────────────┐
│                    Memory Manager                         │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │           Short-term Memory (단기 기억)           │    │
│  │           Redis / In-memory Cache                 │    │
│  │                                                   │    │
│  │  세션ID → {                                       │    │
│  │    대화_이력: [...],                              │    │
│  │    현재_작업: "BOM 검토 중",                      │    │
│  │    임시_결과: {커넥터A: "12핀, 10A"},             │    │
│  │    업로드_파일: "harness_v3.dxf"                  │    │
│  │  }                                                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │           Long-term Memory (장기 기억)            │    │
│  │           SQLite + ChromaDB                       │    │
│  │                                                   │    │
│  │  ① 설계 검토 이력 DB                             │    │
│  │    - 프로젝트명, 날짜, 검토결과, 발견된 문제점     │    │
│  │                                                   │    │
│  │  ② 부품 스펙 라이브러리                           │    │
│  │    - 커넥터, 터미널, 와이어 스펙                   │    │
│  │                                                   │    │
│  │  ③ 표준 규격 문서 (Vector DB)                     │    │
│  │    - KSC, ISO, OEM 기준서                        │    │
│  │    - 과거 보고서                                  │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## Short-term Memory (단기 기억)

### 저장 위치: Redis 또는 Python dict (세션 단위)

### 저장하는 내용

```
{
  "session_id": "abc-123",
  "created_at": "2026-03-28 10:00",

  "conversation": [
    {"role": "user",      "content": "A커넥터 스펙 알려줘"},
    {"role": "assistant", "content": "A커넥터: 12핀, 10A"},
    {"role": "user",      "content": "B하네스에 적용 가능해?"}
  ],

  "current_task": {
    "type": "설계 검토",
    "status": "진행 중",
    "current_step": 3,
    "total_steps": 6
  },

  "temp_data": {
    "uploaded_file": "engine_harness_v3.dxf",
    "extracted_bom": [
      {"part_no": "C-001", "name": "A커넥터", "qty": 4},
      {"part_no": "W-012", "name": "0.5sq 와이어", "qty": 12}
    ]
  }
}
```

### 수명
- 사용자 세션 종료 시 삭제
- 기본 유효 시간: 2시간 (비활성 시)

---

## Long-term Memory (장기 기억)

### ① 설계 검토 이력 DB (SQLite)

```sql
-- 설계 검토 이력 테이블
CREATE TABLE design_reviews (
    id           INTEGER PRIMARY KEY,
    project_name TEXT,          -- 프로젝트명
    review_date  TEXT,          -- 검토일
    file_name    TEXT,          -- 검토 파일
    issues_found INTEGER,       -- 발견된 문제 수
    severity     TEXT,          -- 심각도 (LOW/MID/HIGH)
    result       TEXT,          -- 최종 판정 (PASS/FAIL)
    report       TEXT           -- 보고서 전문
);

-- 부품 이력 테이블
CREATE TABLE part_history (
    part_no    TEXT,
    part_name  TEXT,
    used_in    TEXT,            -- 사용된 프로젝트
    issue      TEXT,            -- 발생한 문제 (있으면)
    date       TEXT
);
```

### ② 부품 스펙 라이브러리 (SQLite)

```sql
-- 커넥터 스펙 테이블
CREATE TABLE connector_specs (
    part_no      TEXT PRIMARY KEY,
    manufacturer TEXT,
    pin_count    INTEGER,
    max_current  REAL,          -- 최대 전류 (A)
    voltage_rate REAL,          -- 정격 전압 (V)
    waterproof   BOOLEAN,       -- 방수 여부
    temp_range   TEXT,          -- 온도 범위
    standard     TEXT           -- 적용 규격
);

-- 와이어 스펙 테이블
CREATE TABLE wire_specs (
    spec_code    TEXT PRIMARY KEY,
    cross_section REAL,         -- 단면적 (sq)
    max_current  REAL,          -- 최대 전류 (A)
    resistance   REAL,          -- 저항 (Ω/m)
    color        TEXT,          -- 색상 코드
    insulation   TEXT           -- 피복 재질
);
```

### ③ 표준 규격 문서 (Vector DB - ChromaDB)

```
저장되는 문서:
  - KSC 규격서 (한국산업표준)
  - ISO 6722 (차량용 저전압 케이블)
  - USCAR-37 (자동차 와이어 하네스 기준)
  - OEM별 설계 가이드라인
  - 과거 설계 검토 보고서

검색 방식:
  "방수 커넥터 최대 전류 기준" 검색
    → 벡터 유사도 계산
    → 관련 규격 문서 TOP 5 반환
    → 에이전트가 해당 내용 참조
```

---

## Memory 활용 시나리오

### 시나리오 1: 반복 작업 학습

```
1차 검토: "C타입 커넥터에서 핀 끼임 문제 발생"
          → Long-term Memory에 저장

2차 검토: 다른 프로젝트, 같은 C타입 커넥터 사용
          → Memory 조회: "이 부품은 핀 끼임 이력 있음"
          → Quality Agent가 사전 경고 발행
```

### 시나리오 2: 대화 맥락 유지

```
사용자: "엔진 하네스 파일 업로드했어"
AI:     "네, engine_harness_v3.dxf 확인했습니다"

사용자: "BOM 뽑아줘"
AI:     [Short-term Memory에서 파일명 참조]
        "engine_harness_v3.dxf에서 BOM을 추출합니다..."
```

### 시나리오 3: 누적 지식 활용

```
표준 규격 Vector DB 조회:
  "40A 이상 전류 회로에 사용 가능한 단면적"
    → ISO 6722 문서에서: "40A = 최소 6.0sq 필요"
    → 자동으로 스펙 검증에 활용
```

---

## Memory 관리 정책

| 항목 | 정책 |
|------|------|
| 단기 기억 보관 기간 | 세션 종료 후 2시간 |
| 장기 기억 최대 보관 | 5년 (법적 요건) |
| 민감 데이터 처리 | 암호화 저장 |
| 백업 주기 | 매일 자동 백업 |
| 검색 응답 시간 | Short-term < 10ms, Long-term < 500ms |
