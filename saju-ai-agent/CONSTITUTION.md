# CONSTITUTION
# 프로젝트 헌법 — 반드시 지켜야 할 규칙

> 이 문서는 모든 기여자(사람 + AI)가 **예외 없이** 따라야 하는 규칙이다.  
> 규칙이 충돌하면 이 문서가 최우선이다.

---

## 0. 존재 이유

```
이 프로젝트는 유튜브 교육용이다.

목표:
  1. 중급 개발자가 "AI 에이전트 시스템"을 처음부터 만드는 과정을 배운다
  2. 모든 코드는 보고 바로 이해할 수 있어야 한다
  3. 복잡한 것보다 명확한 것을 선택한다
```

---

## 1. 파일 규칙 — 절대 원칙

### Rule F-01: 모든 파일은 500라인 미만

```
✅ 허용:  499라인
❌ 금지:  500라인 이상

500라인 초과 시:
  → 파일을 기능 단위로 분리한다
  → 분리가 어려우면 설계를 다시 한다
```

### Rule F-02: 하나의 파일 = 하나의 책임

```
❌ 금지 (나쁜 예):
  orchestrator.py  ← Planner + Memory + Router 모두 포함 (1개 파일)

✅ 허용 (좋은 예):
  orchestrator/
    planner.py     ← 계획 수립만
    memory.py      ← 기억 관리만
    router.py      ← 라우팅만
```

### Rule F-03: 파일 이름은 소문자 + 언더스코어

```
✅ 허용: design_agent.py, bom_agent.py, llm_client.py
❌ 금지: DesignAgent.py, BOMAgent.py, LLMClient.py
```

---

## 2. 코드 규칙

### Rule C-01: 코드는 영어, 주석은 한국어

```python
# 커넥터 스펙을 DB에서 조회합니다
def get_connector_spec(part_no: str) -> dict:
    ...

# ❌ 금지: 변수명/함수명에 한국어 사용
def 커넥터조회(부품번호):  # 잘못됨
    ...
```

### Rule C-02: 타입 힌트 필수 (Python)

```python
# ✅ 모든 함수에 타입 힌트
def calculate_voltage_drop(
    current: float,
    length: float,
    cross_section: float
) -> dict[str, float]:
    ...

# ❌ 금지: 타입 없음
def calculate_voltage_drop(current, length, cross_section):
    ...
```

### Rule C-03: 타입 명시 필수 (TypeScript)

```typescript
// ✅ 모든 props, 함수, 변수에 타입 명시
interface AgentResult {
  agentName: string
  status: "pending" | "running" | "done" | "error"
  result: unknown
}

function runAgent(config: AgentConfig): Promise<AgentResult> { ... }

// ❌ 금지: any 사용
function runAgent(config: any): any { ... }
```

### Rule C-04: 함수는 20라인 이내 (위반 시 분리 필수)

```python
# 20라인 초과 시 → 반드시 더 작은 함수로 분리한다
# 복잡한 로직은 주석으로 단계를 명시

def analyze_bom(file_path: str) -> list[dict]:
    # 1단계: 파일 파싱
    raw_data = parse_excel(file_path)

    # 2단계: 부품번호 검증
    validated = validate_part_numbers(raw_data)

    # 3단계: 스펙 조회 및 결과 반환
    return enrich_with_specs(validated)
```

### Rule C-05: 매직 넘버 금지 — 상수로 선언

```python
# ❌ 금지
if voltage_drop > 0.36:
    ...

# ✅ 허용
MAX_VOLTAGE_DROP_RATIO = 0.03   # 전압 강하 허용 기준: 3%
SUPPLY_VOLTAGE = 12.0           # 기준 전압 (V)
MAX_VOLTAGE_DROP = SUPPLY_VOLTAGE * MAX_VOLTAGE_DROP_RATIO

if voltage_drop > MAX_VOLTAGE_DROP:
    ...
```

---

## 3. 에러 핸들링 규칙

### Rule E-01: 에러는 조용히 삼키지 않는다

```python
# ❌ 금지: 에러를 무시
try:
    result = parse_dxf(file_path)
except Exception:
    pass

# ✅ 허용: 에러를 명확히 처리
try:
    result = parse_dxf(file_path)
except FileNotFoundError:
    # 파일이 없을 때 → 사용자에게 명확한 메시지
    raise AgentError(f"파일을 찾을 수 없습니다: {file_path}")
except DXFParseError as e:
    # 파싱 실패 → 원인 포함하여 전달
    raise AgentError(f"DXF 파싱 실패: {e}")
```

### Rule E-02: 커스텀 예외 클래스 사용

```python
# 에이전트 관련 예외는 AgentError 하위 클래스로 정의
class AgentError(Exception):
    pass

class ParseError(AgentError):
    pass

class ValidationError(AgentError):
    pass

class LLMConnectionError(AgentError):
    pass
```

---

## 4. 테스트 규칙

### Rule T-01: 새 함수 작성 시 테스트 함께 작성

```python
# tests/test_spec_agent.py

def test_voltage_drop_within_limit():
    """전압 강하가 기준치 이내일 때 PASS를 반환한다"""
    result = calculate_voltage_drop(
        current=8.5,
        length=3.2,
        cross_section=1.25
    )
    assert result["status"] == "PASS"

def test_voltage_drop_exceeds_limit():
    """전압 강하가 기준치 초과 시 FAIL을 반환한다"""
    result = calculate_voltage_drop(
        current=20.0,
        length=5.0,
        cross_section=0.5
    )
    assert result["status"] == "FAIL"
```

### Rule T-02: 테스트 파일도 500라인 미만

```
tests/
  test_design_agent.py   ← Design Agent 테스트만
  test_bom_agent.py      ← BOM Agent 테스트만
  test_spec_agent.py     ← Spec Agent 테스트만
  test_orchestrator.py   ← Orchestrator 테스트만
```

### Rule T-03: 테스트 함수 이름은 "무엇을 테스트하는지" 명확하게

```python
# ✅ 좋은 이름
def test_bom_agent_detects_invalid_part_number(): ...
def test_routing_agent_finds_interference_with_exhaust(): ...

# ❌ 나쁜 이름
def test_1(): ...
def test_bom(): ...
```

---

## 5. AI 에이전트 설계 원칙

### Rule A-01: 모든 에이전트는 3개 인터페이스를 가진다

```python
class BaseAgent:
    def run(self, input_data: dict) -> dict:
        """에이전트 실행 (필수 구현)"""
        raise NotImplementedError

    def validate_input(self, input_data: dict) -> bool:
        """입력 유효성 검사 (필수 구현)"""
        raise NotImplementedError

    def get_status(self) -> str:
        """현재 상태 반환 (필수 구현)"""
        raise NotImplementedError
```

### Rule A-02: 에이전트는 LLM에 직접 접근하지 않는다

```
❌ 금지:
  BOMAgent → LLM (직접 호출)

✅ 허용:
  BOMAgent → Orchestrator → LLMClient → LLM
```

### Rule A-03: Orchestrator만이 에이전트 실행 순서를 결정한다

```
에이전트끼리 서로를 직접 호출하지 않는다.
모든 조율은 Orchestrator를 통한다.

❌ 금지: DesignAgent가 내부에서 BOMAgent를 호출
✅ 허용: Orchestrator가 DesignAgent 완료 후 BOMAgent 실행
```

### Rule A-04: 에이전트 결과는 항상 dict 형태로 반환

```python
# ✅ 표준 반환 형식
{
    "agent": "bom_agent",
    "status": "done",          # done / error
    "result": { ... },         # 실제 결과
    "errors": [],              # 에러 목록 (없으면 빈 리스트)
    "duration_ms": 1230        # 처리 시간
}
```

---

## 6. 문서 규칙

### Rule D-01: 새 기능 추가 시 문서 먼저 작성 (Docs First)

```
순서:
  1. harness_eng/ 에 기능 문서 작성
  2. 문서 리뷰 후 코드 작성 시작
  3. 코드 완성 후 문서 업데이트
```

### Rule D-02: 문서도 500라인 미만

### Rule D-03: 모든 문서는 Markdown (.md) 형식

---

## 7. Git 규칙

| 항목 | 규칙 |
|------|------|
| Repository | https://github.com/BogKim2/testsaju2 |
| 기본 브랜치 | `main` |
| 개발 브랜치 | `dev` |
| 기능 브랜치 | `feature/기능명` (예: `feature/bom-agent`) |
| 커밋 메시지 | `타입: 설명` 형식 (Conventional Commits) |

### 커밋 메시지 타입

```
형식: 타입: 설명  (콜론+공백 필수)

타입 목록:
  feat:     새 기능 추가
  fix:      버그 수정
  docs:     문서 변경
  test:     테스트 추가/수정
  refactor: 리팩터링 (기능 변화 없음)
  style:    포맷, 들여쓰기 등

✅ 올바른 예:
  feat: BOM Agent 부품번호 검증 기능 추가
  fix: 전압 강하 계산 공식 오류 수정
  docs: Routing Agent 설계 문서 작성

❌ 잘못된 예:
  [feat] BOM Agent 추가     ← 대괄호 형식 금지
  BOM Agent 추가            ← 타입 없음 금지
```

---

## 8. 위반 시 처리

```
Constitution 위반 발견 시:
  1. 코드 리뷰에서 즉시 지적
  2. 병합(merge) 전에 수정 필수
  3. 긴급 상황이라도 임시 예외는 주석으로 이유 명시

# CONSTITUTION-EXCEPTION: F-01
# 이유: ~~~ 임시로 500라인 초과, 다음 PR에서 분리 예정
```

---

## 요약 체크리스트

코드 작성 전 확인:
- [ ] 이 파일이 500라인 미만인가?
- [ ] 하나의 파일이 하나의 책임만 갖는가?
- [ ] 모든 함수에 타입 힌트가 있는가?
- [ ] 에러를 조용히 삼키지 않는가?
- [ ] 테스트 코드를 함께 작성했는가?
- [ ] 에이전트가 Orchestrator를 통해서만 통신하는가?
- [ ] 에이전트 반환값이 CONTRACTS.md 계약 형식을 따르는가?
- [ ] 커밋 메시지가 `타입: 설명` 형식인가? (대괄호 금지)
