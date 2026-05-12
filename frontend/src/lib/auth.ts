export interface AuthUser {
  email: string;
  name: string;
  token: string;
}

export function saveAuth(user: AuthUser): void {
  localStorage.setItem("sai_token", user.token);
  localStorage.setItem("sai_user", JSON.stringify({ email: user.email, name: user.name }));
}

export function clearAuth(): void {
  localStorage.removeItem("sai_token");
  localStorage.removeItem("sai_user");
}

export function getToken(): string | null {
  return localStorage.getItem("sai_token");
}

export function getUser(): Omit<AuthUser, "token"> | null {
  try {
    const raw = localStorage.getItem("sai_user");
    if (!raw) return null;
    return JSON.parse(raw) as Omit<AuthUser, "token">;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem("sai_token");
}
