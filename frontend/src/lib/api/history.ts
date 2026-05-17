import type { Prediction } from "@/components/dashboard-shell";

const HISTORY_KEY = "sai_history";
const MAX_HISTORY = 50;

function isClient(): boolean {
  return typeof window !== "undefined";
}

export function saveToHistory(prediction: Prediction): void {
  if (!isClient()) return;
  const existing = loadHistory();
  const next = [prediction, ...existing].slice(0, MAX_HISTORY);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
}

export function loadHistory(): Prediction[] {
  if (!isClient()) return [];
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Prediction[];
  } catch {
    return [];
  }
}

export function clearHistory(): void {
  if (!isClient()) return;
  localStorage.removeItem(HISTORY_KEY);
}
