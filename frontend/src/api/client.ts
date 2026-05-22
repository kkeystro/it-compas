const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit,
  retries = 2,
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: { 'Content-Type': 'application/json', ...options?.headers },
        ...options,
      });

      if (!response.ok) {
        let message = `HTTP ${response.status}`;
        try {
          const body = await response.json();
          message = body.detail || message;
        } catch {
          // ignore parse error
        }
        throw new ApiError(response.status, message);
      }

      return response.json();
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));

      // Don't retry client errors (4xx) — they won't magically succeed
      if (err instanceof ApiError && err.status >= 400 && err.status < 500) {
        throw err;
      }

      // Don't retry on last attempt
      if (attempt === retries) {
        throw lastError;
      }

      // Wait before retrying (exponential backoff)
      await delay(1000 * (attempt + 1));
    }
  }

  // Should never reach here, but TypeScript wants a return
  throw lastError || new Error('Unknown error');
}
