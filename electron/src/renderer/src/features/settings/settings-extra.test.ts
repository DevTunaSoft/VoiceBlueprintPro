import { expect, it } from 'vitest';

import { extraSettingsFor } from './settings-page';

it('offers no cloud account or support settings', () => {
  const routes = extraSettingsFor(false).map((item) => item.to);
  expect(routes).not.toContain('/settings/account');
  expect(routes).not.toContain('/settings/support');
});
