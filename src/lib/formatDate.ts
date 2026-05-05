export function formatPublishedDate(value: Date): string {
  const parts = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'UTC',
  }).formatToParts(value);

  const pick = (type: string) => parts.find((part) => part.type === type)?.value ?? '';

  const month = pick('month');
  const day = pick('day');
  const year = pick('year');
  const hour = pick('hour');
  const minute = pick('minute');

  return `${month} ${day}, ${year} ${hour}:${minute} UTC`;
}
