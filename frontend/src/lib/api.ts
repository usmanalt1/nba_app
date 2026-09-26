export function isAccessTokenExpired(token: string) {
  try {
    const payload = token.split('.')[1];
    if (!payload) return true;

    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const claims = JSON.parse(atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, '=')));
    return typeof claims.exp !== 'number' || claims.exp * 1000 <= Date.now();
  } catch {
    return true;
  }
}

export function clearSession() {
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('refresh_token');
}

function redirectToAuth() {
  clearSession();
  if (window.location.pathname !== '/auth') window.location.replace('/auth');
}

async function sendRequest(input: RequestInfo | URL, init: RequestInit, accessToken: string | null) {
  return fetch(input, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(init.headers ?? {}),
    },
  });
}

export async function apiFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
) {
  const accessToken = sessionStorage.getItem('access_token');
  if (accessToken && isAccessTokenExpired(accessToken)) {
    redirectToAuth();
    throw new Error('Session expired');
  }

  const response = await sendRequest(input, init, accessToken);

  if (response.status === 401 && accessToken) {
    redirectToAuth();
  }

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response;
}

export async function registerUser(
  username: string,
  email: string,
  password: string,
) {
  const response = await apiFetch('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });

  return response.json();
}

export async function loginUser(username: string, password: string) {
  const response = await apiFetch('/api/token/pair', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });

  return response.json() as Promise<{ access: string; refresh: string }>;
}