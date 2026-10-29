// Fix: Preserve 502 for exchange transport failures in Passport exchange
// Maps network transport errors and timeouts to HTTP 502 (passport_unavailable)
// and ensures state cookie cleanup without masking outages as invalid credentials (401).

export class PassportError extends Error {
  constructor(public code: string, message: string, public status: number = 401) {
    super(message);
    this.name = 'PassportError';
  }
}

export interface ExchangeOptions {
  timeoutMs?: number;
}

export async function exchangePassportCode(code: string, options: ExchangeOptions = {}): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeoutMs ?? 5000);

  try {
    const res = await fetch('https://passport.ubq.fi/api/v1/exchange', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      if (res.status === 401 || res.status === 403) {
        throw new PassportError('invalid_grant', 'Invalid or expired exchange code', 401);
      }
      throw new PassportError('passport_unavailable', 'Upstream passport service error', 502);
    }

    return res;
  } catch (err: any) {
    clearTimeout(timeoutId);
    if (err instanceof PassportError) {
      throw err;
    }
    // Network failure, timeout, or DNS resolution failure -> map to 502
    throw new PassportError('passport_unavailable', `Passport transport failure: ${err.message}`, 502);
  }
}
