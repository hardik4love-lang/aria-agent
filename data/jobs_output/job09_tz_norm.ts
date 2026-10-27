export function normalizeSlot(startIso: string, endIso: string, timeZone: string) {
  const start = new Date(startIso).getTime();
  const end = new Date(endIso).getTime();
  return {
    utcStart: start,
    utcEnd: end,
    durationMin: Math.round((end - start) / 60000),
    formatted: new Intl.DateTimeFormat('en-US', { timeZone, dateStyle: 'medium', timeStyle: 'short' }).format(new Date(start))
  };
}
