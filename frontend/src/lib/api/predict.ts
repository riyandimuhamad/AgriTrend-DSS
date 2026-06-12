import apiClient from "@/lib/api-client";

// ─── Request ──────────────────────────────────────────────────────────────────
export interface PredictRequest {
  location: string;
  crop_type: string;
  land_area: number;
  planting_date: string; // format YYYY-MM-DD
}

// ─── POST /predict response ───────────────────────────────────────────────────
export interface PredictData {
  prediction_id: string;
  yield_per_ha: number;
  yield_total: number;
  unit: string;
  confidence: number;
  yield_min: number;
  yield_max: number;
  status: "NORMAL" | "CRITICAL";
  crop_type: string;
  region: string;
  timestamp: string;
}

export interface PredictResponse {
  success: boolean;
  data: PredictData;
}

// ─── GET /predict/{id}/advice response ───────────────────────────────────────
export interface AdviceData {
  analysis: string;
  recommendation: string;
}

export interface AdviceResponse {
  success: boolean;
  prediction_id: string;
  data: AdviceData;
}

// ─── Fungsi pemanggil API ─────────────────────────────────────────────────────
export async function submitPrediction(data: PredictRequest): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/v1/ml/predict", data);
  return res.data;
}

export async function fetchAdvice(predictionId: string): Promise<AdviceResponse> {
  const res = await apiClient.get<AdviceResponse>(`/api/v1/ml/predict/${predictionId}/advice`);
  return res.data;
}

// ─── GET /history response ────────────────────────────────────────────────────
export interface HistoryItem {
  prediction_id: string;
  crop_type: string;
  region: string;
  yield_per_ha: number;
  yield_total: number;
  unit: string;
  confidence: number;
  yield_min: number;
  yield_max: number;
  status: string;
  timestamp: string;
}

export interface HistoryResponse {
  success: boolean;
  data: HistoryItem[];
}

export async function fetchHistory(): Promise<HistoryResponse> {
  const res = await apiClient.get<HistoryResponse>("/api/v1/ml/history");
  return res.data;
}
