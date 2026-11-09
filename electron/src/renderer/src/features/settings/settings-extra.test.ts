import { expect, it } from 'vitest';

import { extraSettingsFor } from './settings-page';

it('offers no cloud account settings', () => {
  expect(extraSettingsFor(false)).toEqual([]);
});
