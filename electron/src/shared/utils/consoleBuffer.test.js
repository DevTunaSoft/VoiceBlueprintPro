import { beforeEach, describe, expect, it } from 'vitest';
import {
  clearFrontendLogs,
  formatConsoleMessage,
  getFrontendLogs,
  installConsoleCapture,
  MAX_CONSOLE_MESSAGE_CHARS,
} from './consoleBuffer';

describe('consoleBuffer', () => {
  // installConsoleCapture() wraps console.* exactly once per page load (a
  // module-level `installed` guard) — it must NOT be re-installed or have
  // console.warn restored between tests, or later tests run against the
  // un-wrapped original. Install once; only the ring buffer resets per test.
  installConsoleCapture();

  beforeEach(() => {
    clearFrontendLogs();
  });

  it('captures an ordinary warning', () => {
    console.warn('something genuinely worth seeing');
    expect(getFrontendLogs().some((l) => l.msg.includes('something genuinely worth seeing'))).toBe(
      true,
    );
  });

  it("#975: filters Tauri's benign IPC-fallback warning out of the captured buffer", () => {
    console.warn(
      'IPC custom protocol failed, Tauri will now use the postMessage interface instead',
    );
    expect(getFrontendLogs().some((l) => l.msg.includes('IPC custom protocol failed'))).toBe(false);
  });

  it('does not filter a different warning that merely mentions IPC', () => {
    // Prefix match, not a substring match — only Tauri's exact known message
    // is suppressed; anything else that happens to mention "IPC" is not.
    console.warn('some other IPC warning entirely');
    expect(getFrontendLogs().some((l) => l.msg.includes('some other IPC warning entirely'))).toBe(
      true,
    );
  });
});


describe('strict resource limits for captured frontend logs', () => {
  it('omits very large messages instead of retaining truncated sensitive content', () => {
    const msg = formatConsoleMessage(['secret-key=' + 'x'.repeat(2 * 1024 * 1024)]);
    expect(msg).toContain('Oversized console value omitted');
    expect(msg).not.toContain('secret-key');
    expect(msg.length).toBeLessThanOrEqual(MAX_CONSOLE_MESSAGE_CHARS);
  });

  it('limits object breadth and depth without serializing every entry', () => {
    const huge = Array.from({ length: 100_000 }, (_, index) => index);
    const msg = formatConsoleMessage([{ data: huge, reason: 'test' }]);
    expect(msg).toContain('[more items omitted]');
    expect(msg).toContain('test');
    expect(msg.length).toBeLessThanOrEqual(MAX_CONSOLE_MESSAGE_CHARS);
  });

  it('handles cycles and hostile getters without breaking console capture', () => {
    const obj = { kind: 'error' };
    obj.self = obj;
    Object.defineProperty(obj, 'failing', { enumerable: true, get() { throw Error('secret'); } });
    const msg = formatConsoleMessage([obj]);
    expect(msg).toContain('[Circular]');
    expect(msg).toContain('[unreadable]');
    expect(msg).not.toContain('secret');
  });

  it('redacts tokens and user home paths before retention', () => {
    const msg = formatConsoleMessage(['log /home/alice/cache bearer ' + 's'.repeat(36)]);
    expect(msg).not.toContain('alice');
    expect(msg).not.toContain('s'.repeat(36));
  });
});


it('retains readable Error stacks without retaining huge Error payloads', () => {
  const normal = formatConsoleMessage([new Error('example failure')]);
  expect(normal).toMatch(/^Error: example failure/);
  expect(normal.startsWith('"')).toBe(false);
  const huge = new Error('x'.repeat(30_000));
  expect(formatConsoleMessage([huge])).toContain('Oversized console value omitted');
});

describe('bounded console ring regression', () => {
  it('retains only the newest 500 messages in chronological order', () => {
    clearFrontendLogs();
    for (let i = 0; i < 525; i++) console.debug('ring-entry', i);
    const entries = getFrontendLogs();
    expect(entries).toHaveLength(500);
    expect(entries[0].msg).toContain('ring-entry 25');
    expect(entries[499].msg).toContain('ring-entry 524');
    expect(entries.some((entry) => entry.msg === 'ring-entry 0')).toBe(false);
  });

  it('returns a snapshot so callers cannot change retained log entries by appending', () => {
    clearFrontendLogs();
    console.debug('snapshot-entry');
    const snapshot = getFrontendLogs();
    snapshot.push({ t: 0, level: 'error', msg: 'injected' });
    snapshot[0].msg = 'mutated existing entry';
    expect(getFrontendLogs().some((entry) => entry.msg === 'injected')).toBe(false);
    expect(getFrontendLogs()[0].msg).toBe('snapshot-entry');
  });
});
