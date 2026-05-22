/** Format a number as a percentage string */
export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}

/** Format hours into a readable string */
export function formatHours(hours: number): string {
  if (hours === 0) return '';
  if (hours < 2) return `${hours} час`;
  if (hours < 5) return `${hours} часа`;
  return `${hours} часов`;
}

/** Clamp a value between min and max */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/** Generate a CSS class list filtering out falsy values */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}
