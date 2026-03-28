# Planning — 에이전트 계획 시스템

## Planning이란?
> 복잡한 하네스 엔지니어링 작업을 **실행 가능한 단계로 분해**하는 능력.  
> LLM 혼자 "알아서 해"라고 시키면 실패한다.  
> Planner가 먼저 **무엇을, 어떤 순서로, 누가 할지** 결정해야 한다.

---

## Planning이 없으면 생기는 문제

```
❌ Planning 없음:

사용자: "하네스 설계 파일 전체 검토해줘"
LLM:    (무작위로 대답)
        "일반적으로 하네스 설계 시 주의할 사항은..."
        → 실제 파일 분석 안 함
        → 단계적 검토 없음
        → 누락 항목 발생

✅ Planning 있음:

사용자: "하네스 설계 파일 전체 검토해줘"
Planner:
  Step 1: DXF 파일 파싱 (File Parser Tool)
  Step 2: 회로 구조 파악 (Design Agent)
  Step 3: BOM 추출 및 검증 (BOM Agent)
  Step 4: 전기 스펙 검사 (Spec Agent)
  Step 5: 품질 기준 검토 (Quality Agent)
  Step 6: 종합 보고서 작성 (LLM)
→ 6단계 체계적 실행 보장
```

---

## Plan 데이터 구조

```python
# 하나의 실행 계획 (Plan)
plan = {
    "plan_id": "plan-20260328-001",
    "request":  "하네스 설계 파일 전체 검토",
    "status":   "실행 중",  # 대기 / 실행 중 / 완료 / 실패

    "steps": [
        {
            "step_id":   1,
            "name":      "파일 파싱",
            "agent":     "FileParserTool",
            "input":     "engine_harness_v3.dxf",
            "output":    None,           # 실행 전
            "status":    "완료",
            "depends_on": []             # 선행 단계 없음
        },
        {
            "step_id":   2,
            "name":      "BOM 추출",
            "agent":     "BOMAgent",
            "input":     "step_1의 결과",
            "output":    None,
            "status":    "실행 중",
            "depends_on": [1]            # Step 1 완료 후 실행
        },
        {
            "step_id":   3,
            "name":      "스펙 검증",
            "agent":     "SpecAgent",
            "input":     "step_1의 결과 + step_2의 결과",
            "output":    None,
            "status":    "대기",
            "depends_on": [1, 2]         # Step 1, 2 완료 후 실행
        },
        {
            "step_id":   4,
            "name":      "최종 보고서",
            "agent":     "LLM",
            "input":     "모든 이전 결과",
            "output":    None,
            "status":    "대기",
            "depends_on": [1, 2, 3]
        }
    ]
}
```

---

## Plan 유형별 실행 패턴

### 패턴 A: 순차 실행 (Sequential)

```
Step 1 → Step 2 → Step 3 → 완료

사용 사례:
  - 파일 파싱 → BOM 추출 → 스펙 검증
  - 설계 검토 → 문제 발견 → 수정 제안
```

### 패턴 B: 병렬 실행 (Parallel)

```
      ┌─ Step 2A ─┐
Step 1─┤           ├─ Step 3 → 완료
      └─ Step 2B ─┘

사용 사례:
  - 여러 하네스 모듈 동시 검토
  - BOM 검증 + 경로 분석 동시 실행
  → 시간 절약
```

### 패턴 C: 조건부 실행 (Conditional)

```
Step 1 → [문제 없음?]─── YES ──→ 간단 보고서
                  │
                  └── NO ───→ Step 2 (상세 분석) → Step 3 (수정 제안)

사용 사례:
  - 빠른 검사: 이상 없으면 종료
  - 이상 발견 시: 심층 분석 실행
```

---

## 하네스 엔지니어링 표준 Plan 템플릿

### 템플릿 1: 신규 설계 검토

```
Plan: "신규 하네스 설계 검토"

Step 1: [FileParser]    파일 파싱 및 구조 파악
Step 2: [DesignAgent]   회로 토폴로지 분석
Step 3: [BOMAgent]      부품 목록 추출
Step 4a: [SpecAgent]    전기 스펙 검증   ┐ 병렬 실행
Step 4b: [RoutingAgent] 배선 경로 검토   ┘ (서로 독립)
Step 5: [QualityAgent]  종합 품질 검사 (Step 2~4b 결과 통합)
Step 6: [LLMClient]     종합 검토 보고서 작성 (Orchestrator 경유)

예상 소요 시간: 3~5분
```

### 템플릿 2: BOM 단독 검증

```
Plan: "BOM 검증"

Step 1: [FileParser]  BOM 파일 파싱 (Excel/CSV)
Step 2: [BOMAgent]    부품번호 유효성 검사
Step 3: [BOMAgent]    수량 및 단가 검증
Step 4: [SpecAgent]   부품 스펙 DB 조회
Step 5: [LLM]         BOM 검증 보고서

예상 소요 시간: 1~2분
```

### 템플릿 3: 전기 스펙 계산

```
Plan: "전기 스펙 계산"

Step 1: [SpecAgent]  회로 전류 계산
Step 2: [SpecAgent]  전압 강하 계산
Step 3: [SpecAgent]  와이어 단면적 적정성 검토
Step 4: [SpecAgent]  퓨즈 용량 검증
Step 5: [LLM]        스펙 검토 결과 보고

예상 소요 시간: 1분
```

---

## Plan 실행 모니터링

```
[실행 중인 Plan 상태 화면 예시]

Plan: 신규 하네스 설계 검토
진행: ████████░░ 80%

Step 1: ✅ 파일 파싱 완료       (3초)
Step 2: ✅ 회로 분석 완료       (12초)
Step 3: ✅ BOM 추출 완료        (8초)
Step 4: ✅ 스펙 검증 완료       (15초)
Step 5: 🔄 품질 검사 진행 중...
Step 6: ⏳ 보고서 작성 대기 중

발견된 문제: 3건
  - [HIGH] W-012 와이어 단면적 부족
  - [MID]  커넥터 C-007 방수 등급 미달
  - [LOW]  색상 코드 비표준
```

---

## Planning 개선 메커니즘

### 피드백 루프

```
Plan 실행
   ↓
결과 평가 (성공/실패/부분성공)
   ↓
피드백 기록
   ↓
다음 유사 요청 시 개선된 Plan 적용
```

### 학습되는 것들

| 학습 항목 | 예시 |
|---------|------|
| 에이전트 성능 | "Spec Agent가 이런 질문에 더 빠름" |
| 자주 실패하는 단계 | "DXF v2014 파싱은 3회 재시도 필요" |
| 최적 실행 순서 | "BOM 먼저 → 스펙 검증이 더 효율적" |
