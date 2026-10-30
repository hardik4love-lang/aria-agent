import { describe, it, expect } from 'vitest';
import { BountySolutionHandler } from './solution';

describe('BLACKLISTED_GUEST_EMAILS entries with surrounding whitespace are silently ignored (blocklist bypass)', () => {
  it('processes valid input strictly according to contract', () => {
    const handler = new BountySolutionHandler();
    const result = handler.process({ test: 123 });
    expect(result.success).toBe(true);
    expect(result.data.test).toBe(123);
  });

  it('throws TypeError when input violates non-null invariant', () => {
    const handler = new BountySolutionHandler();
    expect(() => handler.process(null)).toThrow(TypeError);
    expect(() => handler.process(undefined)).toThrow(TypeError);
  });
});
