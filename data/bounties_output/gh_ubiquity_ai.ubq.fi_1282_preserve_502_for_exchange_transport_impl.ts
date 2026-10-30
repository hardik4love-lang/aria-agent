/**
 * Autonomous Fix for: Preserve 502 for exchange transport failures
 * Target Repository: ubiquity/ai.ubq.fi
 * Preserves upstream 502 Bad Gateway responses on transport/network layer failures.
 */

export interface TransportResponse<T = unknown> {
  status: number;
  data?: T;
  error?: string;
  isTransportFailure: boolean;
}

export class ExchangeTransportError extends Error {
  public readonly statusCode: number;
  public readonly isTransportFailure: boolean;
  public readonly originalError?: unknown;

  constructor(message: string, statusCode: number = 502, originalError?: unknown) {
    super(message);
    this.name = "ExchangeTransportError";
    this.statusCode = statusCode;
    this.isTransportFailure = true;
    this.originalError = originalError;
    Object.setPrototypeOf(this, ExchangeTransportError.prototype);
  }
}

export async function executeExchangeRequest<T>(
  requestFn: () => Promise<Response>,
  options: { timeoutMs?: number; retries?: number } = {}
): Promise<TransportResponse<T>> {
  const { timeoutMs = 10000, retries = 2 } = options;
  let attempt = 0;

  while (attempt <= retries) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);

      const resp = await requestFn();
      clearTimeout(timer);

      if (resp.status === 502) {
        const errorText = await resp.text().catch(() => "Upstream 502 Bad Gateway");
        throw new ExchangeTransportError(
          `Exchange transport returned 502: ${errorText}`,
          502
        );
      }

      if (!resp.ok) {
        return {
          status: resp.status,
          error: await resp.text().catch(() => `HTTP error ${resp.status}`),
          isTransportFailure: false
        };
      }

      const data = (await resp.json()) as T;
      return { status: resp.status, data, isTransportFailure: false };
    } catch (err: unknown) {
      attempt++;
      if (attempt > retries) {
        if (err instanceof ExchangeTransportError) {
          throw err;
        }
        throw new ExchangeTransportError(
          `Exchange transport failure after ${retries} attempts: ${((err as Error)?.message || "Unknown transport error")}`,
          502,
          err
        );
      }
    }
  }

  throw new ExchangeTransportError("Exchange transport unreachable", 502);
}
