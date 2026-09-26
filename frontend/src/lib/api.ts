export async function apiFetch(
  input: RequestInfo | URL,
  init: RequestInit = {},
) {
  const accessToken = sessionStorage.getItem('access_token');

  const response = await fetch(input, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...(init.headers ?? {}),
    },
  });

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