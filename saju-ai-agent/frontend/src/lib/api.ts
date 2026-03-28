// 백엔드 FastAPI 연동 함수 모음
import { getToken } from "@/lib/auth";
import type {
  LoginRequest,
  LoginResponse,
  AnalyzeStartResponse,
  AnalyzeStatusResponse,
  FullResultResponse,
  HistoryItem,
} from "@/types/harness";

// Vite 환경변수 사용 (import.meta.env)
const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8010";

// 인증 헤더
function authHeaders(): HeadersInit {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// 에러 응답 처리
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error((err as { message?: string }).message ?? "요청 실패");
  }
  return res.json() as Promise<T>;
}

// 로그인
export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<LoginResponse>(res);
}

// 하네스 파일 분석 시작
export async function analyzeHarness(
  file: File,
  projectName: string
): Promise<AnalyzeStartResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("project_name", projectName);
  formData.append("version", "1.0");
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  return handleResponse<AnalyzeStartResponse>(res);
}

// 분석 상태 조회
export async function getAnalyzeStatus(
  sessionId: string
): Promise<AnalyzeStatusResponse> {
  const res = await fetch(`${API_BASE}/analyze/${sessionId}/status`, {
    headers: authHeaders(),
  });
  return handleResponse<AnalyzeStatusResponse>(res);
}

// 전체 결과 조회
export async function getResult(
  sessionId: string
): Promise<FullResultResponse> {
  const res = await fetch(`${API_BASE}/analyze/${sessionId}/result`, {
    headers: authHeaders(),
  });
  return handleResponse<FullResultResponse>(res);
}

// 에이전트별 결과 조회
export async function getAgentResult(
  sessionId: string,
  agentName: string
): Promise<Record<string, unknown>> {
  const res = await fetch(
    `${API_BASE}/analyze/${sessionId}/result/${agentName}`,
    { headers: authHeaders() }
  );
  return handleResponse<Record<string, unknown>>(res);
}

// 분석 이력 조회
export async function getHistory(): Promise<HistoryItem[]> {
  const res = await fetch(`${API_BASE}/history`, {
    headers: authHeaders(),
  });
  return handleResponse<HistoryItem[]>(res);
}
