# Quality Agent — 품질 검사 에이전트

## 역할
> 하네스 설계가 **품질 기준과 표준 규격을 만족하는지** 종합 검사하는 에이전트.  
> 다른 에이전트들의 분석 결과를 취합하여 최종 합격/불합격 판정을 내린다.

---

## 담당 범위

| 항목 | 설명 |
|------|------|
| 설계 규칙 검사 (DRC) | 색상 코드, 핀 매칭, 라벨 등 |
| 기계적 기준 검사 | 굴곡 반경, 번들 직경, 클램프 간격 |
| 방수/방진 기준 | 커넥터 IP 등급, 그로멧 적용 여부 |
| 내열 기준 | 와이어/커넥터 온도 등급 |
| 체결 기준 | 커넥터 잠금 구조, 풀림 방지 |
| 종합 판정 | PASS / CONDITIONAL PASS / FAIL |

---

## 품질 검사 체크리스트

### 1. 전기적 품질

```
□ E-QC-01: 전압 강하 허용 기준 이내
□ E-QC-02: 와이어 단면적 전류 용량 충족
□ E-QC-03: 퓨즈 용량 적정 (1.25배 안전계수)
□ E-QC-04: 접지 회로 저항 기준 이내 (< 0.1Ω)
□ E-QC-05: CAN 버스 종단 저항 120Ω 적용 여부
```

### 2. 기계적 품질

```
□ M-QC-01: 최소 굴곡 반경 ≥ 와이어 직경 × 6
□ M-QC-02: 번들 직경 < 클램프 내경의 90%
□ M-QC-03: 클램프 간격 ≤ 300mm (일반), ≤ 200mm (진동 부위)
□ M-QC-04: 커넥터 고정 나사 토크 규정 준수
□ M-QC-05: 번들 테이프 감기 각도 50% 이상 겹침
```

### 3. 환경 기준

```
□ ENV-QC-01: 엔진룸 부품 내열 등급 ≥ +125°C
□ ENV-QC-02: 외장 배선 방수 등급 ≥ IP54
□ ENV-QC-03: 수침 부위 커넥터 ≥ IP67
□ ENV-QC-04: 화학약품 내성 (오일, 냉각수) 확인
□ ENV-QC-05: UV 내성 피복 외장 적용 여부
```

### 4. 도면/문서 품질

```
□ D-QC-01: 모든 커넥터에 ID 라벨 있음
□ D-QC-02: 와이어 색상 코드 표준 준수 (KSC)
□ D-QC-03: 부품번호 BOM과 도면 일치
□ D-QC-04: 회로 번호 체계 일관성
□ D-QC-05: 설계 버전/날짜 기입
```

---

## 입력 / 출력

```
입력:
  - Design Agent 결과
  - BOM Agent 결과
  - Spec Agent 결과
  - (직접 업로드 파일도 가능)

출력:
  {
    "overall_result": "CONDITIONAL PASS",
    "inspection_date": "2026-03-28",
    "project": "엔진 하네스 v3.1",

    "results_by_category": {
      "electrical": {"pass": 4, "warn": 1, "fail": 0},
      "mechanical":  {"pass": 5, "warn": 0, "fail": 0},
      "environmental": {"pass": 3, "warn": 2, "fail": 0},
      "documentation": {"pass": 4, "warn": 0, "fail": 1}
    },

    "issues": [
      {
        "id":       "E-QC-03",
        "severity": "WARNING",
        "item":     "퓨즈 용량",
        "detail":   "LAMP-FR-L 회로 퓨즈 10A, 권장 12A",
        "action":   "설계 담당자 확인 후 조정 요망"
      },
      {
        "id":       "D-QC-02",
        "severity": "FAIL",
        "item":     "와이어 색상 코드",
        "detail":   "W-045: 색상 'PK' 비표준 색상 사용",
        "action":   "표준 색상으로 변경 필수"
      }
    ],

    "statistics": {
      "total_checks": 20,
      "pass": 15,
      "warning": 3,
      "fail": 2,
      "pass_rate": "75%"
    },

    "verdict": {
      "result": "CONDITIONAL PASS",
      "condition": "FAIL 항목 2건 수정 후 재검토 필요",
      "next_action": "설계 수정 → 재검토 신청"
    }
  }
```

---

## 심각도 기준

| 심각도 | 기준 | 조치 |
|--------|------|------|
| **FAIL** | 안전 위험 또는 법규 위반 | 즉시 수정 후 재검토 필수 |
| **WARNING** | 성능 저하 가능 | 설계 담당자 확인 필요 |
| **INFO** | 최적화 제안 | 차기 버전 반영 권고 |
| **PASS** | 기준 충족 | 조치 불필요 |

---

## 에이전트 내부 처리 흐름

```
1. 다른 에이전트 결과 수집
      - Design Agent: DRC 결과
      - BOM Agent: 부품 검증 결과
      - Spec Agent: 전기 계산 결과

2. 체크리스트 항목별 매핑
      → 각 에이전트 결과를 20개 체크 항목에 배분

3. 항목별 판정
      → PASS / WARNING / FAIL 할당

4. 종합 판정 결정
      FAIL ≥ 1개 → "FAIL" 또는 "CONDITIONAL PASS"
      WARNING만   → "CONDITIONAL PASS"
      모두 PASS   → "PASS"

5. LLM에 최종 보고서 작성 요청
      "검사 결과를 요약하고 수정 우선순위를 제안해줘"
```

---

## 사용 도구

| 도구 | 용도 |
|------|------|
| DesignRuleCheck | 설계 규칙 자동 검사 |
| StandardQuery | 품질 기준 규격 조회 |
| ReportGenerator | 품질 검사 보고서 생성 |
| HistoryQuery | 유사 문제 과거 사례 조회 |
| LLM | 판정 근거 및 조치 제안 작성 |

---

## 품질 기준

| 지표 | 기준 |
|------|------|
| 체크리스트 커버리지 | 20개 항목 전체 검사 |
| 판정 정확도 | 98% 이상 |
| 보고서 생성 시간 | 60초 이내 |
| 지원 표준 | ISO, USCAR, KSC, OEM 내규 |
