import { describe, it, expect } from 'vitest';
import { BountySolutionHandler } from './solution';

describe('Blank page on iOS/iPadOS 15 (Safari < 16.4): Vite's default build target drops marked's lookbehind fallback; front components need Safari 16.4+', () => {
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
