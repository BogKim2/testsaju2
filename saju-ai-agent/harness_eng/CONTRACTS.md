# CONTRACTS — 에이전트 인수인계 계약

> 에이전트 간 데이터를 넘길 때 **어떤 형식으로, 무엇을 전달하는지**를 정의한다.
> Orchestrator는 이 계약을 보고 데이터를 조립해서 다음 에이전트에 전달한다.

---

## 에이전트 완료 판단 기준

에이전트는 아래 조건을 **모두** 만족해야 `"status": "done"`이 된다.

| 에이전트 | 완료 조건 |
|---------|---------|
| Design Agent | connectors, bundles, drc_issues 모두 추출 완료 |
| BOM Agent | 전체 행 처리 완료 (오류 행 포함) |
| Spec Agent | 모든 회로 전기 계산 완료 |
| Quality Agent | 20개 체크리스트 항목 판정 완료 |
| Routing Agent | 모든 경로 분석 및 간섭 검출 완료 |

> 부분 완료도 `"status": "done"` 으로 반환한다. 단, errors 리스트에 기록한다.

---

## 표준 반환 형식 (모든 에이전트 공통)

```python
# CONSTITUTION Rule A-04 준수
{
    "agent":       "design_agent",          # 에이전트 이름
    "status":      "done",                  # done | error
    "result":      { ... },                 # 아래 각 에이전트 명세 참조
    "errors":      [],                      # 에러 목록 (없으면 빈 리스트)
    "duration_ms": 8200                     # 처리 시간
}
```

---

## 에이전트별 result 계약

### Design Agent → (output)

```python
{
    "summary": {
        "total_connectors": int,
        "total_wires":      int,
        "total_splices":    int,
        "circuit_count":    int
    },
    "connectors": [
        {
            "id":       str,        # "J1"
            "type":     str,        # "12핀 방수"
            "location": str,        # "엔진룸 좌측"
            "pins": [
                {"pin": int, "circuit": str, "color": str}
            ]
        }
    ],
    "bundles": [
        {
            "id":       str,        # "B-001"
            "wires":    list[str],  # ["W-001", "W-002"]
            "diameter": float,      # mm
            "length":   float       # mm
        }
    ],
    "drc_issues": [
        {"type": str, "description": str}  # type: WARNING | FAIL
    ]
}
```

### BOM Agent 입력 ← (Design Agent result 활용)

```python
# Orchestrator가 조립:
{
    "source":      "dxf" | "excel",
    "file_path":   str,
    "design_data": design_agent_result  # Design Agent 결과 전달 (선택)
}
```

### BOM Agent → (output)

```python
{
    "bom": [
        {
            "line_no":     int,
            "part_no":     str,
            "name":        str,
            "qty":         int,
            "unit_price":  int,
            "total_price": int,
            "spec":        dict | None,
            "status":      "정상" | "오류" | "경고",
            "error":       str | None
        }
    ],
    "summary": {
        "total_items": int,
        "total_cost":  int,
        "errors":      int,
        "warnings":    int
    }
}
```

### Spec Agent 입력 ← (Design + BOM 결과 활용)

```python
# Orchestrator가 조립:
{
    "circuits": [
        {
            "circuit_id":    str,       # "IGN-001"
            "current":       float,     # A (BOM 스펙에서 추출)
            "length":        float,     # m (Design 번들 길이에서 추출)
            "cross_section": float,     # mm² (BOM 스펙에서 추출)
            "wire_material": "copper"
        }
    ]
}
```

### Spec Agent → (output)

```python
{
    "circuits": [
        {
            "circuit_id":    str,
            "voltage_drop":  float,     # V
            "resistance":    float,     # Ω
            "status":        "PASS" | "FAIL" | "WARN",
            "message":       str        # 상세 설명
        }
    ],
    "fuse_checks": [
        {
            "fuse_id": str,
            "rated_A": float,
            "actual_A": float,
            "status":  "PASS" | "FAIL"
        }
    ]
}
```

### Quality Agent 입력 ← (Design + BOM + Spec 결과 통합)

```python
# Orchestrator가 3개 결과를 통합하여 전달:
{
    "design_result": design_agent_result,
    "bom_result":    bom_agent_result,
    "spec_result":   spec_agent_result
}
```

### Quality Agent → (output)

```python
{
    "overall_verdict": "PASS" | "CONDITIONAL_PASS" | "FAIL",
    "pass_rate":       float,       # 0.0 ~ 1.0
    "checklist": [
        {
            "id":       str,        # "QC-001"
            "item":     str,        # 검사 항목명
            "verdict":  "PASS" | "WARN" | "FAIL",
            "detail":   str,
            "action":   str         # 권고 조치
        }
    ]
}
```

### Routing Agent 입력 ← (Design 결과 활용)

```python
# Orchestrator가 조립:
{
    "bundles":      design_result["bundles"],
    "vehicle_zones": [
        {"zone": "엔진룸", "heat_risk": True},
        {"zone": "도어", "heat_risk": False}
    ]
}
```

### Routing Agent → (output)

```python
{
    "interference_risks": [
        {
            "bundle_id":   str,
            "risk_type":   str,     # "고온부 근접" | "날카로운 모서리"
            "severity":    "HIGH" | "MED" | "LOW",
            "location":    str,
            "suggestion":  str
        }
    ],
    "optimized_routes": [
        {
            "bundle_id":       str,
            "current_length":  float,   # mm
            "optimal_length":  float,   # mm
            "saving_mm":       float
        }
    ],
    "cost_saving_estimate": int     # 원 단위
}
```

---

## 에이전트 실패 처리 계약

```
에이전트가 실패하면:
  1. status = "error" 로 반환
  2. errors 리스트에 원인 기록
  3. result = {} (빈 dict) 반환

Orchestrator 처리:
  - 해당 에이전트에 의존하는 다음 에이전트는 "SKIP" 처리
  - Quality Agent는 가용한 결과만으로 부분 판정 수행
  - 최종 응답에 "일부 에이전트 실패로 결과가 불완전함" 명시
```

```python
# 실패 시 반환 예시
{
    "agent":    "spec_agent",
    "status":   "error",
    "result":   {},
    "errors":   ["회로 전류 데이터 누락: IGN-001 circuit_id 없음"],
    "duration_ms": 120
}
```
