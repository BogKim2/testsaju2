// JWT 토큰 관리 (sessionStorage)
const ACCESS_KEY = "harness_access_token";

export function saveToken(token: string): void {
  sessionStorage.setItem(ACCESS_KEY, token);
}

export function getToken(): string | null {
  return sessionStorage.getItem(ACCESS_KEY);
}

export function clearToken(): void {
  sessionStorage.removeItem(ACCESS_KEY);
}

export function isLoggedIn(): boolean {
  return getToken() !== null;
}
