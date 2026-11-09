// @vitest-environment node
import { expect, it } from 'vitest';
import { join } from 'node:path';
import { scopedStorage, scopedStorageEnv } from './storage-scope';

const root = join('E:', 'VoiceBlueprint');

it('puts data, models and every temp variable under the chosen location (#2971)', () => {
  const s = scopedStorage(root);
  expect(scopedStorageEnv(root)).toEqual({
    VOICEBLUEPRINT_DATA_DIR: s.data,
    VOICEBLUEPRINT_CACHE_DIR: s.models,
    TEMP: s.temp,
    TMP: s.temp,
    TMPDIR: s.temp,
  });
  expect(s.data.startsWith(root) && s.models.startsWith(root) && s.temp.startsWith(root)).toBe(true);
});

it('keeps values the user already set explicitly', () => {
  const out = scopedStorageEnv(root, { VOICEBLUEPRINT_CACHE_DIR: 'D:\\models', TEMP: 'D:\\t' });
  expect(out.VOICEBLUEPRINT_CACHE_DIR).toBeUndefined();
  expect(out.TEMP).toBeUndefined();
  expect(out.VOICEBLUEPRINT_DATA_DIR).toBe(scopedStorage(root).data);
});
