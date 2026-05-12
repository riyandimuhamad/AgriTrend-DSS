import type { Prediction } from "@/components/dashboard-shell";

const HISTORY_KEY = "sai_history";
const MAX_HISTORY = 50;

export function saveToHistory(prediction: Prediction): void {
  const existing = loadHistory();
  const next = [prediction, ...existing].slice(0, MAX_HISTORY);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
}

export function loadHistory(): Prediction[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Prediction[];
  } catch {
    return [];
  }
}

export function clearHistory(): void {
  localStorage.removeItem(HISTORY_KEY);
}
