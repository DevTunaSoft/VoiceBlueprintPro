// Ring buffer for frontend console messages. Settings "Logs > Frontend" tab
// reads from here. Installed once in main.jsx so every console.* is captured
// without breaking the DevTools output.

import { scrubText } from './scrub';

const MAX = 500;
export const MAX_CONSOLE_MESSAGE_CHARS = 4096;
const MAX_FIELDS = 8;
const MAX_NESTING = 3;
const MAX_VISITED_VALUES = 48;
const OVERSIZED = '[Oversized console value omitted]';
const buf = [];

/**
 * Small, bounded diagnostic preview. Object and array traversal are capped
 * before JSON serialization, so a console.log of a giant object cannot
 * retain that object inside our log ring.
 */
function preview(value, state, depth = 0) {
  if (state.remaining-- <= 0) return '[truncated]';
  if (typeof value === 'string') return value.length > 1024 ? OVERSIZED : value;
  if (value == null || typeof value === 'number' || typeof value === 'boolean') return value;
  if (typeof value !== 'object') return String(value).slice(0, 1024);
  if (value instanceof Error) {
    const detail = value.stack || `${value.name}: ${value.message}`;
    return detail.length > MAX_CONSOLE_MESSAGE_CHARS ? OVERSIZED : detail;
  }
  if (state.seen.has(value)) return '[Circular]';
  if (depth >= MAX_NESTING) return '[nested object omitted]';
  state.seen.add(value);
  if (Array.isArray(value)) {
    const output = [];
    for (let index = 0; index < Math.min(value.length, MAX_FIELDS); index++) {
      try { output.push(preview(value[index], state, depth + 1)); }
      catch { output.push('[unreadable]'); }
    }
    if (value.length > MAX_FIELDS) output.push('[more items omitted]');
    return output;
  }
  const output = {};
  let count = 0;
  for (const key in value) {
    if (!Object.prototype.hasOwnProperty.call(value, key)) continue;
    if (count++ >= MAX_FIELDS) {
      output['[more fields omitted]'] = true;
      break;
    }
    try { output[key.slice(0, 128)] = preview(value[key], state, depth + 1); }
    catch { output[key.slice(0, 128)] = '[unreadable]'; }
  }
  return output;
}

/** Bounded, redacted console capture; never retains giant console arguments. */
export function formatConsoleMessage(args) {
  const state = { remaining: MAX_VISITED_VALUES, seen: new WeakSet() };
  const rendered = [];
  for (let i = 0; i < Math.min(args.length, MAX_FIELDS); i++) {
    try {
      const value = args[i];
      rendered.push(
        typeof value === 'string'
          ? value.length > MAX_CONSOLE_MESSAGE_CHARS ? OVERSIZED : value
          : JSON.stringify(preview(value, state)) ?? '[unprintable]',
      );
    } catch {
      rendered.push('[unprintable]');
    }
  }
  if (args.length > MAX_FIELDS) rendered.push('[more arguments omitted]');
  return scrubText(rendered.join(' ')).slice(0, MAX_CONSOLE_MESSAGE_CHARS);
}


// Tauri's own internal IPC fallback (#975): on some Windows configurations
// the custom-protocol IPC probe fails once at startup and Tauri logs this
// exact console.warn before silently — and successfully — falling back to
// postMessage + WebSocket. It's benign and fires at most once per launch,
// but as a captured console.warn it spuriously flips the Logs footer's
// Frontend pill to "1 warning" on every affected launch. Filtered at the
// capture source (not the display layer) so it never enters the ring
// buffer or a copied diagnostic dump either.
const BENIGN_WARNING_PREFIXES = ['IPC custom protocol failed'];

function push(level, args) {
  if (level === 'warn' && typeof args[0] === 'string') {
    if (BENIGN_WARNING_PREFIXES.some((p) => args[0].startsWith(p))) return;
  }
  const msg = formatConsoleMessage(args);
  buf.push({ t: Date.now(), level, msg });
  if (buf.length > MAX) buf.shift();
}

let installed = false;
export function installConsoleCapture() {
  if (installed || typeof window === 'undefined') return;
  installed = true;
  ['log', 'info', 'warn', 'error', 'debug'].forEach((level) => {
    const orig = console[level].bind(console);
    console[level] = (...args) => {
      try {
        push(level, args);
      } catch {}
      orig(...args);
    };
  });
  window.addEventListener('error', (e) => {
    push('error', [
      `[uncaught] ${e.message}`,
      e.filename ? `at ${e.filename}:${e.lineno}:${e.colno}` : '',
    ]);
  });
  window.addEventListener('unhandledrejection', (e) => {
    push('error', ['[unhandledrejection]', e.reason]);
  });
}

export function getFrontendLogs() {
  return buf.slice();
}

export function clearFrontendLogs() {
  buf.length = 0;
}
