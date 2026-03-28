# Plans — 개발 계획

## Phase 1: 아키텍처 설계 ✅ 완료
- [x] Orchestrator 구조 설계
- [x] Memory 시스템 설계
- [x] Planning 시스템 설계
- [x] Tool Control 설계
- [x] 5개 에이전트 스펙 정의

## Phase 2: Orchestrator 구현 (예정)
- [ ] Planner 모듈 구현
- [ ] Memory Manager 구현 (Redis + SQLite)
- [ ] Task Router 구현
- [ ] 에이전트 인터페이스 정의

## Phase 3: Tool 구현 (예정)
- [ ] DXFParser (ezdxf 기반)
- [ ] ExcelParser (openpyxl 기반)
- [ ] PartDBQuery (SQLite)
- [ ] 전기 계산 도구 (VoltageCalc, WireSizeCalc, FuseCalc)
- [ ] DesignRuleCheck
- [ ] Vector DB 구축 (ChromaDB + 표준 규격 문서)

## Phase 4: 에이전트 구현 (예정)
- [ ] Design Agent
- [ ] BOM Agent
- [ ] Spec Agent
- [ ] Quality Agent
- [ ] Routing Agent

## Phase 5: FastAPI 서버 (예정)
- [ ] REST API 엔드포인트
- [ ] 파일 업로드 처리
- [ ] 진행 상태 스트리밍 (SSE)
- [ ] 인증 (JWT)

## Phase 6: Frontend (예정)
- [ ] 파일 업로드 UI
- [ ] 분석 진행 상태 표시
- [ ] 에이전트별 결과 탭
- [ ] 보고서 다운로드
