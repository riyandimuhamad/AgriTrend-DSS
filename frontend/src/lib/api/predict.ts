import apiClient from "@/lib/api-client";

export interface PredictRequest {
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
  crop_type: string;
  kode_kabupaten_kota?: number | null;
  nama_kabupaten_kota?: string | null;
  insight_mode: "market_only" | "agronomy_plus_market";
}

export interface PredictCoordinates {
  latitude: number;
  longitude: number;
  region: string;
}

export interface PredictResult {
  predicted_yield_ton_per_ha: number;
  market_trend: string;
  coordinates: PredictCoordinates;
}

export interface PredictResponse {
  prediction: PredictResult;
  insight: string;
  insight_structured: Record<string, unknown>;
}

export async function submitPrediction(data: PredictRequest): Promise<PredictResponse> {
  const res = await apiClient.post<PredictResponse>("/api/v1/ml/predict", data);
  return res.data;
}
