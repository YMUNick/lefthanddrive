export function normalizeLanguage(value) {
  return value === 'zh-Hant' ? 'zh-Hant' : 'en';
}

export function singaporeDate(now = new Date()) {
  const parts = new Intl.DateTimeFormat('en', {
    timeZone: 'Asia/Singapore', year: 'numeric', month: '2-digit', day: '2-digit'
  }).formatToParts(now);
  const part = type => parts.find(p => p.type === type).value;
  return `${part('year')}-${part('month')}-${part('day')}`;
}

export function classifyShow(show, today = singaporeDate()) {
  if (show.date.length === 7) {
    const month = today.slice(0, 7);
    return show.date < month ? 'past' : show.date === month ? 'announced' : 'upcoming';
  }
  return show.date < today ? 'past' : show.date === today ? 'today' : 'upcoming';
}

export function sortShows(shows) {
  return [...shows].sort((a, b) => b.date.localeCompare(a.date));
}
