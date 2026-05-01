/**
 * Utility function to merge Tailwind CSS classes
 * Combines multiple class strings and handles conditional classes
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}
