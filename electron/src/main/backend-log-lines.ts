/** Bounds the memory retained while decoding logs from a child process.
 *
 * A child may write megabytes without a newline or several lines in one chunk.
 * Never build an unbounded pending string or a huge split() array: consume a
 * chunk in a single pass and retain at most MAX_BACKEND_LOG_LINE_CHARS per line.
 * Oversized lines are omitted entirely (a truncated token may evade scrubbing).
 */
export const MAX_BACKEND_LOG_LINE_CHARS = 8 * 1024;
export const OVERSIZED_BACKEND_LOG_LINE =
  '[Backend output line omitted: exceeded 8192 characters]';

export function createBoundedLogLineReader(onLine: (line: string) => void): {
  write(chunk: string): void;
  finish(): void;
} {
  let pending = '';
  let oversized = false;

  const append = (chunk: string, start: number, end: number): void => {
    if (oversized || start === end) return;
    if (end - start > MAX_BACKEND_LOG_LINE_CHARS - pending.length) {
      pending = '';
      oversized = true;
      return;
    }
    pending += chunk.slice(start, end);
  };

  const flush = (): void => {
    if (oversized) onLine(OVERSIZED_BACKEND_LOG_LINE);
    else if (pending) onLine(pending);
    pending = '';
    oversized = false;
  };

  return {
    write(chunk: string): void {
      let start = 0;
      for (let index = 0; index < chunk.length; index++) {
        const char = chunk.charCodeAt(index);
        if (char !== 10 && char !== 13) continue;
        append(chunk, start, index);
        flush();
        start = index + 1;
      }
      append(chunk, start, chunk.length);
    },
    finish(): void {
      flush();
    },
  };
}
