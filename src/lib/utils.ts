/**
 * Utility functions for the Adsomnia Talk-to-Data agent
 */

/**
 * Generate a unique ID for messages
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Format a date for display
 */
export function formatTime(date: Date): string {
  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Format currency values
 */
export function formatCurrency(value: number, currency: string = "EUR"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(value);
}

/**
 * Format percentage values
 */
export function formatPercent(value: number): string {
  return `${value.toFixed(2)}%`;
}

/**
 * Format large numbers with commas
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US").format(value);
}

/**
 * Parse natural language date expressions to date range
 */
export function parseDateRange(expression: string): { from: Date; to: Date } {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const expr = expression.toLowerCase().trim();

  if (expr === "today") {
    return { from: today, to: today };
  }

  if (expr === "yesterday") {
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    return { from: yesterday, to: yesterday };
  }

  if (expr === "last week" || expr === "last 7 days") {
    const from = new Date(today);
    from.setDate(from.getDate() - 7);
    const to = new Date(today);
    to.setDate(to.getDate() - 1);
    return { from, to };
  }

  if (expr === "this week") {
    const from = new Date(today);
    from.setDate(from.getDate() - from.getDay());
    return { from, to: today };
  }

  if (expr === "last 30 days") {
    const from = new Date(today);
    from.setDate(from.getDate() - 30);
    return { from, to: today };
  }

  if (expr === "this month") {
    const from = new Date(today.getFullYear(), today.getMonth(), 1);
    return { from, to: today };
  }

  if (expr === "last month") {
    const from = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    const to = new Date(today.getFullYear(), today.getMonth(), 0);
    return { from, to };
  }

  // Default to last 7 days
  const from = new Date(today);
  from.setDate(from.getDate() - 7);
  return { from, to: today };
}

/**
 * Format date as YYYY-MM-DD for API calls
 */
export function formatDateForAPI(date: Date): string {
  return date.toISOString().split("T")[0];
}






