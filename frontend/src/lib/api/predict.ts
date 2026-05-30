import apiClient from "@/lib/api-client";

// ─── Request — hanya 4 field dari form petani ─────────────────────────────────
export interface PredictRequest {
  location: string; // nama kabupaten/kota
  crop_type: string; // "padi" | "jagung"
  land_area: number; // hektar
  planting_date: string; // format YYYY-MM-DD
}

// ─── Response — struktur dari backend ────────────────────────────────────────
export interface PredictCoordinates {
  latitude: number;
  longitude: number;
  region: string;
}

export interface PredictResult {
  predicted_yield_ton_per_ha: number;
  market_trend: string;
  confidence?: number; // 0–100, opsional dari backend
  coordinates: PredictCoordinates;
}

export interface PredictResponse {
  prediction: PredictResult;
  insight: string;
  insight_structured: Record<string, unknown>;
}

// ─── Fungsi pemanggil API ─────────────────────────────────────────────────────
export async function submitPrediction(data: PredictRequest): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/v1/ml/predict", data);
  return res.data;
}
