import apiClient from "@/lib/api-client";

// ─── Request — hanya 4 field dari form petani ─────────────────────────────────
export interface PredictRequest {
  location: string;
  crop_type: string;
  land_area: number;
  planting_date: string; // format YYYY-MM-DD
}

// ─── Response — struktur aktual dari backend ──────────────────────────────────
export interface PredictData {
  yield_per_ha: number;
  yield_total: number;
  unit: string;
  confidence: number;
  yield_min: number;
  yield_max: number;
  status: "NORMAL" | "PANEN_BERLIMPAH" | "CRITICAL";
  crop_type: string;
  region: string;
  ai_advice: string;
  timestamp: string;
}

export interface PredictResponse {
  success: boolean;
  data: PredictData;
}

// ─── Fungsi pemanggil API ─────────────────────────────────────────────────────
export async function submitPrediction(data: PredictRequest): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/v1/ml/predict", data);
  return res.data;
}
