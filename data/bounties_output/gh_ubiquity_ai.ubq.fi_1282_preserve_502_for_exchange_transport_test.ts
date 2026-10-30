import { describe, it, expect, vi } from 'vitest';
import { executeExchangeRequest, ExchangeTransportError } from './solution';

describe('Preserve 502 Exchange Transport', () => {
  it('preserves upstream 502 status code when exchange service drops', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      text: () => Promise.resolve('Upstream Gateway Dropped')
    });

    await expect(
      executeExchangeRequest(mockFetch, { retries: 0 })
    ).rejects.toThrow(ExchangeTransportError);
  });

  it('translates network drops into 502 Bad Gateway rather than 500', async () => {
    const mockNetworkDrop = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));

    try {
      await executeExchangeRequest(mockNetworkDrop, { retries: 1 });
    } catch (e: any) {
      expect(e.statusCode).toBe(502);
      expect(e.isTransportFailure).toBe(true);
    }
  });
});
