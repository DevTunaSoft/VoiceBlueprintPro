import { describe, expect, it, vi } from 'vitest';
import {
  createBoundedLogLineReader,
  MAX_BACKEND_LOG_LINE_CHARS,
  OVERSIZED_BACKEND_LOG_LINE,
} from './backend-log-lines';

describe('bounded child log decoder', () => {
  it('joins partial lines, handles CR/LF and flushes the trailing line', () => {
    const emit = vi.fn();
    const reader = createBoundedLogLineReader(emit);
    reader.write('first\r\nsecond\nthird');
    reader.write(' part\rlast');
    reader.finish();
    reader.finish();
    expect(emit.mock.calls.map(([line]) => line)).toEqual([
      'first', 'second', 'third part', 'last',
    ]);
  });

  it('retains a line exactly at the limit', () => {
    const emit = vi.fn();
    const line = 'a'.repeat(MAX_BACKEND_LOG_LINE_CHARS);
    const reader = createBoundedLogLineReader(emit);
    reader.write(line);
    reader.finish();
    expect(emit).toHaveBeenCalledExactlyOnceWith(line);
  });

  it('drops oversized lines entirely, then recovers for later lines', () => {
    const emit = vi.fn();
    const reader = createBoundedLogLineReader(emit);
    reader.write('sensitive-fragment-'.repeat(MAX_BACKEND_LOG_LINE_CHARS));
    reader.write('\nhealthy\r\n');
    expect(emit.mock.calls.map(([line]) => line)).toEqual([
      OVERSIZED_BACKEND_LOG_LINE, 'healthy',
    ]);
    expect(emit.mock.calls[0][0]).not.toContain('sensitive');
  });

  it('bounds lines that cross chunks without storing the growing string', () => {
    const emit = vi.fn();
    const reader = createBoundedLogLineReader(emit);
    for (let i = 0; i < 20; i++) reader.write('x'.repeat(600));
    reader.write('\nnext\n');
    reader.finish();
    expect(emit.mock.calls.map(([line]) => line)).toEqual([
      OVERSIZED_BACKEND_LOG_LINE, 'next',
    ]);
  });

  it('handles a large chunk without producing an unbounded array of lines', () => {
    const output: string[] = [];
    const reader = createBoundedLogLineReader((line) => output.push(line));
    reader.write('x'.repeat(1024 * 1024) + '\nlast');
    reader.finish();
    expect(output).toEqual([OVERSIZED_BACKEND_LOG_LINE, 'last']);
  });
});
