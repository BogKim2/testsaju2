# BOM Agent — 부품 목록 관리 에이전트

## 역할
> BOM(Bill of Materials, 부품 목록)을 **추출, 검증, 비교**하는 에이전트.  
> 부품번호 유효성, 수량, 단가, 스펙 적합성을 종합 검토한다.

---

## 담당 범위

| 항목 | 설명 |
|------|------|
| BOM 추출 | 도면/Excel에서 부품 목록 자동 추출 |
| 부품번호 검증 | 사내 부품 DB와 대조하여 유효성 확인 |
| 수량 검증 | 도면의 부품 수와 BOM 수량 일치 여부 |
| 단가 계산 | 부품 단가 합산, 총 원가 계산 |
| BOM 비교 | 이전 버전과의 변경 사항 비교 |
| 대체 부품 제안 | 단종/이슈 부품 → 대체품 추천 |

---

## 입력 / 출력

```
입력:
  - BOM Excel 파일 (.xlsx, .csv)
  - 또는 DXF 도면 (부품 목록 자동 추출)
  - 이전 버전 BOM (비교용, 선택)

출력:
  {
    "bom": [
      {
        "line_no":   1,
        "part_no":   "C-001",
        "name":      "방수 커넥터 12핀",
        "qty":       4,
        "unit_price": 1200,
        "total_price": 4800,
        "spec": {
          "max_current": 10.0,
          "waterproof":  true,
          "ip_rating":   "IP67"
        },
        "status": "정상"
      },
      {
        "line_no":   2,
        "part_no":   "W-012-ERR",
        "name":      "0.5sq 와이어",
        "qty":       12,
        "status":    "오류",
        "error":     "부품번호가 DB에 없습니다"
      }
    ],

    "summary": {
      "total_items":       24,
      "total_cost":        125400,
      "errors":            1,
      "warnings":          2,
      "changed_from_prev": 3
    },

    "changes": [
      {
        "part_no": "C-005",
        "change_type": "수량 변경",
        "old_qty": 2,
        "new_qty": 4
      }
    ]
  }
```

---

## 에이전트 내부 처리 흐름

```
1. 입력 감지
      → 파일 형식 판별 (Excel? DXF? CSV?)

2. BOM 파싱
      → Excel: ExcelParser Tool → 행별 부품 정보 추출
      → DXF: DXFParser + 도면 내 부품 리스트 레이어 추출

3. 부품번호 유효성 검사 (각 행 처리)
      → PartNoValidator Tool 호출
      → 사내 DB와 대조
      → 유효: 스펙 데이터 추가
      → 무효: 오류 플래그

4. 스펙 조회
      → PartDBQuery Tool: 각 부품의 상세 스펙 가져오기
      → 스펙 없는 부품 → "스펙 미등록" 경고

5. 수량 합산 및 원가 계산
      → 단위 수량 × 단가 = 합계
      → 전체 합산

6. 이전 버전 비교 (있는 경우)
      → 추가/삭제/변경 항목 식별
      → 변경 사항 목록 생성

7. Orchestrator에 LLM 요청 위임
      → 결과 dict를 Orchestrator에 반환
      → Orchestrator가 LLMClient를 통해 최종 요약 생성
      → (에이전트가 LLM을 직접 호출하지 않는다 — CONSTITUTION Rule A-02)
```

---

## BOM 오류 유형

```
오류 (ERROR) → 즉시 수정 필요:
  E-001: 부품번호 DB에 없음
  E-002: 단종된 부품 사용
  E-003: 수량 0 또는 음수
  E-004: 필수 컬럼 누락 (부품번호, 수량)

경고 (WARNING) → 확인 권장:
  W-001: 유사 부품번호 존재 (오타 의심)
  W-002: 수량이 이전 버전 대비 2배 이상 증가
  W-003: 단가가 이전 대비 50% 이상 변동
  W-004: 스펙 DB에 해당 부품 미등록

정보 (INFO):
  I-001: 신규 추가 부품
  I-002: 삭제된 부품
  I-003: 대체 추천 부품 존재
```

---

## 대체 부품 추천 로직

```
단종 부품 감지 시:
  1. 사내 DB에서 동일 스펙 부품 검색
     → 핀 수, 최대 전류, 방수 등급 동일한 것 우선
  2. 없으면 표준 규격 기준으로 동급 추천
  3. 가격 비교 후 최저가 우선 제안

예시:
  기존: C-OLD-12P (단종)
  추천: C-NEW-12P (동일 스펙, 가격 -15%)
       C-ALT-12P  (동등 품질, 가격 -8%)
```

---

## 사용 도구

| 도구 | 용도 |
|------|------|
| ExcelParser | BOM Excel 파싱 |
| DXFParser | 도면에서 BOM 추출 |
| PartNoValidator | 부품번호 유효성 검사 |
| PartDBQuery | 부품 스펙 조회 |
| HistoryQuery | 이전 버전 BOM 조회 |
| ReportGenerator | BOM 보고서 생성 |

> ⚠️ LLM은 직접 호출 금지. 이 Agent는 결과 dict를 Orchestrator에 반환하고,
> Orchestrator가 LLMClient를 통해 최종 요약을 생성한다. (CONSTITUTION Rule A-02)

---

## 품질 기준

| 지표 | 기준 |
|------|------|
| 부품번호 검증 정확도 | 99% 이상 |
| Excel 파싱 성공률 | 95% 이상 |
| 처리 속도 (100행 BOM) | 10초 이내 |
| 지원 파일 형식 | .xlsx, .xls, .csv |
