// 하네스 엔지니어링 AI Agent TypeScript 타입 정의

export type AgentName = "design" | "bom" | "spec" | "quality" | "routing";
export type AgentStatus = "pending" | "running" | "done" | "error";
export type QualityVerdict = "PASS" | "CONDITIONAL_PASS" | "FAIL";
export type IssueSeverity = "FAIL" | "WARNING" | "INFO";

// 로그인
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// 분석 시작 응답
export interface AnalyzeStartResponse {
  session_id: string;
  status: string;
  message: string;
}

// 에이전트 진행 정보
export interface AgentProgress {
  name: AgentName;
  status: AgentStatus;
  started_at: string | null;
  completed_at: string | null;
}

// 분석 상태
export interface AnalyzeStatusResponse {
  session_id: string;
  status: AgentStatus;
  agents: AgentProgress[];
}

// 품질 이슈
export interface QualityIssue {
  id: string;
  severity: IssueSeverity;
  item: string;
  detail: string;
  action: string;
}

// 품질 검사 결과
export interface QualityResult {
  overallResult: QualityVerdict;
  passRate: number;
  issues: QualityIssue[];
}

// BOM 항목
export interface BomItem {
  partNumber: string;
  description: string;
  quantity: number;
  unit: string;
  standard: string;
  status: "OK" | "WARNING" | "ERROR";
}

// BOM 결과
export interface BomResult {
  totalItems: number;
  passItems: number;
  items: BomItem[];
}

// 전기 스펙 항목
export interface SpecItem {
  wireName: string;
  current: number;
  voltage: number;
  voltageDrop: number;
  isAcceptable: boolean;
}

// 전기 스펙 결과
export interface SpecResult {
  items: SpecItem[];
  summary: string;
}

// 전체 분석 결과
export interface FullResultResponse {
  session_id: string;
  project_name: string;
  status: AgentStatus;
  summary: string;
  agents: {
    design: Record<string, unknown> | null;
    bom: BomResult | null;
    spec: SpecResult | null;
    quality: QualityResult | null;
    routing: Record<string, unknown> | null;
  };
}

// 이력 항목
export interface HistoryItem {
  session_id: string;
  project_name: string;
  status: AgentStatus;
  created_at: string;
  summary: string;
}
