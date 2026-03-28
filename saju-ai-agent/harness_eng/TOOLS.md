# Tools — 에이전트 도구 제어 시스템

## Tool Control이란?
> 에이전트가 **외부 시스템과 상호작용**하는 방법.  
> LLM은 텍스트만 처리한다. 실제 파일을 읽거나, DB를 조회하거나, 계산을 하려면 도구(Tool)가 필요하다.  
> Tool Control은 에이전트가 올바른 도구를 올바른 타이밍에 사용하도록 관리한다.

---

## 도구 사용의 원칙

```
에이전트가 할 수 있는 것:
  - 텍스트 분석
  - 패턴 인식
  - 논리적 추론
  - 계획 수립

에이전트가 할 수 없는 것:
  - DXF 파일 직접 읽기 ──→ FileParser Tool 필요
  - DB에서 부품 조회    ──→ DBQuery Tool 필요
  - 전기 계산 수행      ──→ Calculator Tool 필요
  - 설계 규칙 검사      ──→ Validator Tool 필요
```

---

## 전체 도구 목록

```
┌─────────────────────────────────────────────────────┐
│                    Tool Registry                     │
│                                                      │
│  입력/파싱 도구                                       │
│  ├── 📄 DXFParser        CAD 도면 파싱               │
│  ├── 📊 ExcelParser      BOM/스펙 Excel 파싱         │
│  ├── 📋 PDFParser        PDF 도면/규격서 파싱         │
│  └── 📁 FileDetector     파일 형식 자동 감지          │
│                                                      │
│  조회 도구                                            │
│  ├── 🔍 PartDBQuery      부품 스펙 DB 조회            │
│  ├── 📚 StandardQuery    표준 규격 조회               │
│  └── 🗂️ HistoryQuery     과거 설계 이력 조회          │
│                                                      │
│  계산 도구                                            │
│  ├── ⚡ VoltageCalc      전압 강하 계산               │
│  ├── 🔌 CurrentCalc      전류 계산                    │
│  ├── 📏 WireSizeCalc     와이어 단면적 계산            │
│  └── 🔧 FuseCalc         퓨즈 용량 계산               │
│                                                      │
│  검증 도구                                            │
│  ├── ✅ DesignRuleCheck  설계 규칙 검사 (DRC)         │
│  ├── 🏷️ PartNoValidator  부품번호 유효성 검사          │
│  └── 📐 RouteValidator   경로 규칙 검사               │
│                                                      │
│  출력 도구                                            │
│  ├── 📝 ReportGenerator  보고서 생성                  │
│  └── 📤 ExcelExporter    Excel 출력                  │
└─────────────────────────────────────────────────────┘
```

---

## 각 도구 상세 명세

### 1. DXFParser — CAD 도면 파싱

```
목적:    DXF 형식의 하네스 도면 파일을 읽어 구조 데이터로 변환

입력:    .dxf 파일 경로

출력:    {
           "layers": ["WIRE", "CONNECTOR", "LABEL"],
           "entities": [
             {"type": "LINE", "start": [0,0], "end": [100,0], "layer": "WIRE"},
             {"type": "INSERT", "name": "CONN_A", "layer": "CONNECTOR"}
           ],
           "connectors": [...],
           "wires": [...]
         }

사용 라이브러리: ezdxf
오류 처리:       지원 버전(DXF R12~R2018), 깨진 파일 감지
```

### 2. ExcelParser — BOM 파싱

```
목적:    Excel 형식의 BOM(부품 목록) 파일 파싱

입력:    .xlsx / .xls / .csv 파일 경로

출력:    [
           {"row": 1, "part_no": "C-001", "name": "A커넥터", "qty": 4, "unit_price": 1200},
           {"row": 2, "part_no": "W-012", "name": "0.5sq 와이어", "qty": 12, "unit_price": 80}
         ]

사용 라이브러리: openpyxl, pandas
컬럼 자동 감지: 첫 행 헤더 자동 인식
```

### 3. PartDBQuery — 부품 스펙 조회

```
목적:    부품번호로 스펙 DB에서 상세 정보 조회

입력:    part_no = "C-001"

출력:    {
           "part_no":    "C-001",
           "name":       "방수 커넥터 12핀",
           "max_current": 10.0,   (A)
           "voltage":    12.0,    (V)
           "waterproof": True,
           "ip_rating":  "IP67",
           "temp_range": "-40°C ~ +125°C",
           "standard":   "ISO 6722"
         }

캐시:    자주 조회되는 부품 메모리 캐시 (응답 빠름)
오류:    부품번호 없을 시 "부품을 찾을 수 없음" 반환
```

### 4. VoltageCalc — 전압 강하 계산

```
목적:    와이어 길이, 전류, 단면적으로 전압 강하 계산

입력:    {
           "current":        15.0,   (A)
           "length":         3.5,    (m, 왕복이므로 실제 ×2)
           "cross_section":  2.0,    (sq, mm²)
           "wire_material":  "copper"
         }

계산식:  전압강하(V) = 전류 × 저항
         저항(Ω) = 저항률 × 길이 / 단면적
         구리 저항률 = 0.01724 Ω·mm²/m

출력:    {
           "voltage_drop":  0.905,  (V)
           "resistance":    0.060,  (Ω)
           "is_acceptable": False,  (기준: 0.36V 이하, 12V × 3% = 0.36V)
           "warning":       "전압 강하 0.905V — 허용 기준 0.36V 초과"
         }
         
         ※ 전압강하 허용 기준: 공급전압(12V) × 3% = 0.36V
           → CONSTITUTION Rule C-05의 MAX_VOLTAGE_DROP과 동일
```

### 5. DesignRuleCheck — 설계 규칙 검사

```
목적:    하네스 설계가 표준 설계 규칙을 만족하는지 검사

입력:    설계 데이터 (DXFParser 출력)

검사 규칙:
  Rule 1: 와이어 색상 코드 → KSC 또는 ISO 표준 준수
  Rule 2: 커넥터 핀 수 매칭 → 양쪽 커넥터 핀 수 일치
  Rule 3: 최소 굴곡 반경 → 와이어 직경 × 6 이상
  Rule 4: 번들 직경 → 클램프 내경 이상
  Rule 5: 라벨 누락 → 모든 커넥터에 라벨 필수

출력:    [
           {"rule": "Rule 1", "status": "PASS"},
           {"rule": "Rule 2", "status": "FAIL",
            "detail": "J5 커넥터 - 핀 수 불일치 (좌:12핀, 우:10핀)"},
           {"rule": "Rule 3", "status": "WARN",
            "detail": "W-012 와이어 굴곡 반경 불충분"}
         ]
```

### 6. ReportGenerator — 보고서 생성

```
목적:    분석 결과를 구조화된 보고서로 변환

입력:    {
           "project": "엔진 하네스 v3",
           "date":    "2026-03-28",
           "results": [...에이전트 분석 결과...],
           "issues":  [...발견된 문제...]
         }

출력 형식:
  - Markdown 텍스트 (API 응답)
  - Excel 파일 (요청 시)
  - PDF 파일 (요청 시)

포함 내용:
  1. 검토 개요 (파일명, 날짜, 담당자)
  2. 발견된 문제 목록 (심각도별 정렬)
  3. 전기 스펙 계산 결과
  4. 권장 조치 사항
  5. 합격/불합격 판정
```

---

## 도구 호출 방식

### 에이전트 → 도구 호출 흐름

```python
# 에이전트가 도구를 호출하는 방식 (의사코드)

class BOMAgent:
    def run(self, file_path):

        # 1. 파일 형식 감지
        file_type = FileDetector.detect(file_path)
        # → "excel"

        # 2. 적합한 파서 선택
        if file_type == "excel":
            bom_data = ExcelParser.parse(file_path)

        # 3. 각 부품번호로 DB 조회
        for row in bom_data:
            spec = PartDBQuery.query(row["part_no"])
            row["spec"] = spec

        # 4. 유효성 검사
        issues = PartNoValidator.validate(bom_data)

        return {"bom": bom_data, "issues": issues}
```

---

## 도구 오류 처리 전략

| 오류 상황 | 대응 방법 |
|---------|---------|
| 파일 읽기 실패 | 오류 메시지 → 사용자에게 파일 재업로드 요청 |
| DB 연결 실패 | 캐시 데이터 사용 → 없으면 "DB 연결 불가" 안내 |
| 계산 오류 | 입력값 범위 검사 → 이상 시 사용자에게 확인 요청 |
| 도구 타임아웃 | 30초 후 타임아웃 → 에이전트에 실패 알림 |
| 미지원 파일 형식 | 지원 형식 목록 안내 |
