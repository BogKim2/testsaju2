// 백엔드 API 클라이언트
import { getToken } from "./auth";
import type {
  AnalyzeRequest,
  AnalysisStatus,
  SajuResult,
  HistoryItem,
} from "../types/saju";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8020";

// 공통 fetch 래퍼
async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const resp = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: "서버 오류" }));
    throw new Error(error.detail || `HTTP ${resp.status}`);
  }
  return resp.json();
}

// 로그인
export async function login(email: string, password: string) {
  return apiFetch<{ access_token: string; token_type: string; email: string }>(
    "/auth/login",
    { method: "POST", body: JSON.stringify({ email, password }) }
  );
}

// 사주 분석 시작
export async function startAnalysis(req: AnalyzeRequest) {
  return apiFetch<{ session_id: string; message: string }>("/saju/analyze", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

// 분석 진행 상태 조회
export async function getAnalysisStatus(sessionId: string) {
  return apiFetch<AnalysisStatus>(`/saju/${sessionId}/status`);
}

// 분석 결과 조회
export async function getAnalysisResult(sessionId: string) {
  return apiFetch<SajuResult>(`/saju/${sessionId}/result`);
}

// 분석 이력 조회
export async function getHistory() {
  return apiFetch<{ items: HistoryItem[] }>("/history");
}

// 헬스체크
export async function healthCheck() {
  return apiFetch<{ status: string }>("/health");
}
