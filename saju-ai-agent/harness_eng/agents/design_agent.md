# Design Agent — 하네스 설계 분석 에이전트

## 역할
> 하네스 도면(DXF/PDF)을 읽어 **전체 회로 구조를 파악**하고  
> 설계 의도와 레이아웃을 분석하는 에이전트.

---

## 담당 범위

| 항목 | 설명 |
|------|------|
| 회로 토폴로지 분석 | 어떤 장치들이 어떻게 연결되어 있는지 파악 |
| 커넥터 맵핑 | 각 커넥터의 위치, 핀 배열, 연결 관계 |
| 번들 구성 분석 | 와이어 묶음(번들)의 구성 파악 |
| 분기 포인트 식별 | Y형 분기, 스플라이스 위치 파악 |
| 설계 규칙 검사 | 기본 DRC(Design Rule Check) 수행 |

---

## 입력 / 출력

```
입력:
  - DXF 파일 (필수)
  - PDF 도면 (선택)
  - 설계 버전 정보 (선택)

출력:
  {
    "summary": {
      "total_connectors": 24,
      "total_wires":      87,
      "total_splices":    12,
      "circuit_count":    15
    },
    "connectors": [
      {
        "id":       "J1",
        "type":     "12핀 방수",
        "location": "엔진룸 좌측",
        "pins": [
          {"pin": 1, "circuit": "IGN", "color": "R"},
          {"pin": 2, "circuit": "GND", "color": "B"}
        ]
      }
    ],
    "bundles": [
      {
        "id":       "B-001",
        "wires":    ["W-001", "W-002", "W-003"],
        "diameter": 12.5,  (mm)
        "length":   1200   (mm)
      }
    ],
    "drc_issues": [
      {"type": "WARNING", "description": "J5 라벨 누락"}
    ]
  }
```

---

## 에이전트 내부 처리 흐름

```
1. DXFParser Tool 호출
      → 도면 파일 파싱 → 레이어/엔티티 데이터 추출

2. 커넥터 인식
      → INSERT 엔티티에서 커넥터 심볼 식별
      → 각 커넥터의 핀 수, 유형 파악

3. 와이어 추적 (Wire Tracing)
      → LINE/POLYLINE 엔티티 추적
      → 시작점-끝점 연결로 회로 토폴로지 생성

4. 번들 분석
      → 동일 경로의 와이어들을 번들로 그룹화
      → 번들 직경 계산

5. DesignRuleCheck Tool 호출
      → 기본 설계 규칙 검사

6. Orchestrator에 결과 반환
      → 분석 결과 dict를 Orchestrator에 반환
      → Orchestrator가 LLMClient를 통해 설계 인사이트 생성 요청
      → (에이전트 LLM 직접 호출 금지 — CONSTITUTION Rule A-02)
```

---

## 하네스 엔지니어링 도메인 지식

### 회로 분류 체계

```
전원 회로 (Power Circuit)
  - 배터리 공급 회로
  - 점화 공급 회로
  - 상시 전원 회로

신호 회로 (Signal Circuit)
  - 센서 신호 회로
  - 통신 버스 (CAN, LIN)
  - 스위치 신호 회로

접지 회로 (Ground Circuit)
  - 섀시 접지
  - 신호 접지
```

### 커넥터 명명 규칙

```
J  : 주 커넥터 (Junction)
    → J1, J2, J3...

C  : 보조 커넥터 (Connector)
    → C1, C2...

SP : 스플라이스 (Splice)
    → SP1, SP2...

G  : 접지 포인트 (Ground)
    → G1, G2...
```

---

## 사용 도구

| 도구 | 용도 |
|------|------|
| DXFParser | CAD 도면 파싱 |
| PDFParser | PDF 도면 파싱 |
| DesignRuleCheck | 설계 규칙 검사 |
| HistoryQuery | 유사 설계 이력 조회 |

> ⚠️ LLM은 직접 호출 금지. 결과 dict를 Orchestrator에 반환하고,
> Orchestrator가 LLMClient를 통해 인사이트를 생성한다. (CONSTITUTION Rule A-02)

---

## LLM 프롬프트 전략

```
System:
  "당신은 자동차 와이어 하네스 설계 전문가입니다.
   DXF 도면 분석 결과를 바탕으로 설계 품질을 평가하세요."

User:
  "다음 하네스 설계 분석 결과를 검토해 주세요:
   [구조 데이터 삽입]

   검토 항목:
   1. 설계 구조의 적절성
   2. 잠재적 문제점
   3. 개선 권고 사항"
```

---

## 품질 기준

| 지표 | 기준 |
|------|------|
| 파싱 정확도 | 95% 이상 |
| 커넥터 인식률 | 98% 이상 |
| DRC 완료 시간 | 30초 이내 |
| 지원 DXF 버전 | R12 ~ R2018 |
