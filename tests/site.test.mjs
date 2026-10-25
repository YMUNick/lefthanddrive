import test from 'node:test';
import assert from 'node:assert/strict';

const core = await import('../assets/core.mjs').catch(() => ({}));

test('past shows never remain upcoming after their Singapore calendar date', () => {
  assert.equal(typeof core.classifyShow, 'function');
  assert.equal(core.classifyShow({date:'2026-05-23'}, '2026-10-26'), 'past');
  assert.equal(core.classifyShow({date:'2026-10-26'}, '2026-10-26'), 'today');
  assert.equal(core.classifyShow({date:'2027-04-16'}, '2026-10-26'), 'upcoming');
});
test('month-only dates retain uncertainty until that month ends', () => {
  assert.equal(typeof core.classifyShow, 'function');
  assert.equal(core.classifyShow({date:'2025-10'}, '2025-10-15'), 'announced');
  assert.equal(core.classifyShow({date:'2025-10'}, '2025-11-01'), 'past');
});
test('show archive is chronological without mutating the editable content', () => {
  assert.equal(typeof core.sortShows, 'function');
  const shows=[{date:'2025-06-28'}, {date:'2026-05-23'}, {date:'2025-10'}];
  assert.deepEqual(core.sortShows(shows).map(x=>x.date), ['2026-05-23','2025-10','2025-06-28']);
  assert.equal(shows[0].date, '2025-06-28');
});
test('only supported languages can be restored from storage or a link', () => {
  assert.equal(typeof core.normalizeLanguage, 'function');
  assert.equal(core.normalizeLanguage('zh-Hant'), 'zh-Hant');
  for (const value of [null, '', 'fr', '<script>']) assert.equal(core.normalizeLanguage(value),'en');
});
test('dates use Singapore time even on a host in another timezone', () => {
  assert.equal(typeof core.singaporeDate, 'function');
  assert.equal(core.singaporeDate(new Date('2026-10-25T17:00:00Z')), '2026-10-26');
});
