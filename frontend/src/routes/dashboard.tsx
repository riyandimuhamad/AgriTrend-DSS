import { createFileRoute } from "@tanstack/react-router";
import { Sparkles, Brain, CloudSun, Leaf, MapPin, TrendingUp, Calendar } from "lucide-react";
import { DashboardShell, type Prediction, STATUS_CONF } from "@/components/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ApiError } from "@/components/ui/api-error";
import { submitPrediction } from "@/lib/api/predict";
import { saveToHistory, loadHistory } from "@/lib/api/history";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/dashboard")({
  head: () => ({ meta: [{ title: "Dashboard — Agri Trend DSS" }] }),
  component: Dashboard,
});

// ─── Helper ──────────────────────────────────────────────────────────────────

function marketTrendToStatus(trend: string): Prediction["status"] {
  if (trend.includes("naik") || trend.includes("berlimpah")) return "BERLIMPAH";
  if (trend.includes("mitigasi") || trend.includes("gagal") || trend.includes("turun"))
    return "GAGAL";
  return "NORMAL";
}

function extractAdvice(insightStructured: Record<string, unknown>, insightRaw: string): string {
  const s = insightStructured;
  const advice =
    (s.advice as string) ??
    (s.saran as string) ??
    (s.rekomendasi as string) ??
    (s.recommendation as string) ??
    (s.summary as string) ??
    null;
  if (advice) return advice;
  try {
    const parsed = JSON.parse(insightRaw) as Record<string, unknown>;
    return (
      (parsed.advice as string) ??
      (parsed.saran as string) ??
      (parsed.rekomendasi as string) ??
      insightRaw.slice(0, 300)
    );
  } catch {
    return insightRaw.slice(0, 300);
  }
}

// ─── Komponen utama ───────────────────────────────────────────────────────────

function Dashboard() {
  const [history, setHistory] = useState<Prediction[]>([]);
  const [current, setCurrent] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // 4 field form — sesuai kebutuhan backend
  const [location, setLocation] = useState("");
  const [cropType, setCropType] = useState("padi");
  const [landArea, setLandArea] = useState("2.5");
  const [plantingDate, setPlantingDate] = useState(
    () => new Date().toISOString().slice(0, 10), // default: hari ini
  );

  useEffect(() => {
    setHistory(loadHistory());
  }, []);

  const onSubmit = async (e: { preventDefault(): void }) => {
    e.preventDefault();
    setLoading(true);
    setCurrent(null);
    setApiError(null);

    try {
      const data = await submitPrediction({
        location: location.trim(),
        crop_type: cropType,
        land_area: parseFloat(landArea),
        planting_date: plantingDate,
      });

      const yieldVal = data.prediction.predicted_yield_ton_per_ha;
      const status = marketTrendToStatus(data.prediction.market_trend);
      const advice = extractAdvice(data.insight_structured, data.insight);
      const region = data.prediction.coordinates?.region ?? location.trim() ?? "Tidak diketahui";

      const pred: Prediction = {
        id: crypto.randomUUID(),
        location: region,
        crop: cropType,
        area: parseFloat(landArea),
        date: new Date().toISOString().slice(0, 10),
        yield: parseFloat(yieldVal.toFixed(2)),
        status,
        confidence: data.prediction.confidence ?? 85,
        advice,
      };

      setCurrent(pred);
      saveToHistory(pred);
      setHistory(loadHistory());
    } catch (err: unknown) {
      setApiError((err as Error)?.message ?? "Gagal mendapatkan prediksi. Coba lagi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardShell>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Prediksi Panen Baru</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Masukkan data lahan — sistem akan mengambil data cuaca dan tanah secara otomatis.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* ── Form ─────────────────────────────────────────────────────── */}
        <div className="lg:col-span-2">
          <form
            onSubmit={onSubmit}
            className="rounded-3xl border border-border/60 bg-card p-6 shadow-[var(--shadow-soft)]"
          >
            <h2 className="text-lg font-semibold">Data Lahan</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Data cuaca dan kondisi tanah diambil otomatis berdasarkan lokasi Anda.
            </p>

            <div className="mt-5 space-y-4">
              {/* Lokasi */}
              <div className="space-y-2">
                <Label htmlFor="loc">
                  <MapPin className="mr-1 inline h-3.5 w-3.5" />
                  Lokasi Lahan
                </Label>
                <Input
                  id="loc"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Contoh: Subang, Jawa Barat"
                  required
                  className="h-11 rounded-xl"
                />
              </div>

              {/* Jenis tanaman */}
              <div className="space-y-2">
                <Label htmlFor="crop">
                  <Leaf className="mr-1 inline h-3.5 w-3.5" />
                  Jenis Tanaman
                </Label>
                <Select value={cropType} onValueChange={setCropType}>
                  <SelectTrigger id="crop" className="h-11 rounded-xl">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="padi">Padi</SelectItem>
                    <SelectItem value="jagung">Jagung</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Luas lahan */}
              <div className="space-y-2">
                <Label htmlFor="area">Luas Lahan (hektar)</Label>
                <Input
                  id="area"
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="100"
                  value={landArea}
                  onChange={(e) => setLandArea(e.target.value)}
                  required
                  className="h-11 rounded-xl"
                />
              </div>

              {/* Tanggal tanam */}
              <div className="space-y-2">
                <Label htmlFor="planting-date">
                  <Calendar className="mr-1 inline h-3.5 w-3.5" />
                  Tanggal Mulai Tanam
                </Label>
                <Input
                  id="planting-date"
                  type="date"
                  value={plantingDate}
                  onChange={(e) => setPlantingDate(e.target.value)}
                  required
                  className="h-11 rounded-xl"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="mt-6 h-12 w-full rounded-xl bg-[image:var(--gradient-hero)] text-base font-semibold shadow-[var(--shadow-soft)] hover:opacity-95"
            >
              {loading ? (
                "Menganalisis..."
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" /> Prediksi Sekarang
                </>
              )}
            </Button>
          </form>

          {/* Info otomatis */}
          <div className="mt-4 rounded-2xl border border-border/60 bg-muted/30 p-4">
            <p className="text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">Data yang diambil otomatis:</span>{" "}
              Cuaca dari Open-Meteo, kondisi tanah dari database Jawa Barat, dan baseline panen dari
              BPS.
            </p>
          </div>
        </div>

        {/* ── Hasil ────────────────────────────────────────────────────── */}
        <div className="lg:col-span-3">
          {apiError && (
            <div className="mb-4">
              <ApiError message={apiError} onRetry={() => setApiError(null)} />
            </div>
          )}
          {loading && <SkeletonResult />}
          {!loading && !current && !apiError && <EmptyState />}
          {!loading && current && <ResultCard pred={current} />}

          {/* Riwayat */}
          {history.length > 0 && (
            <div className="mt-6 rounded-3xl border border-border/60 bg-card p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold">Riwayat Prediksi</h3>
                <span className="text-xs text-muted-foreground">{history.length} prediksi</span>
              </div>
              <div className="mt-4 divide-y divide-border/60">
                {history.slice(0, 5).map((h) => {
                  const conf = STATUS_CONF[h.status];
                  return (
                    <div key={h.id} className="flex items-center justify-between gap-3 py-3">
                      <div className="min-w-0">
                        <div className="truncate text-sm font-medium capitalize">
                          {h.crop} · {h.area} ha
                        </div>
                        <div className="truncate text-xs text-muted-foreground">
                          {h.location} · {h.date}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold">
                          {h.yield}{" "}
                          <span className="text-xs font-normal text-muted-foreground">ton/ha</span>
                        </div>
                        <span
                          className={`mt-0.5 inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold ${conf.bg} ${conf.color}`}
                        >
                          {conf.label}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardShell>
  );
}

// ─── Sub-komponen ─────────────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="flex h-full min-h-[400px] flex-col items-center justify-center rounded-3xl border border-dashed border-border bg-card p-10 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <Sparkles className="h-8 w-8 text-primary" />
      </div>
      <h3 className="mt-5 text-lg font-semibold">Siap memprediksi panen Anda</h3>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        Isi form di sebelah kiri lalu klik <strong>Prediksi Sekarang</strong>. Hasil akan muncul di
        sini dalam beberapa detik.
      </p>
    </div>
  );
}

function SkeletonResult() {
  return (
    <div className="rounded-3xl border border-border/60 bg-card p-8">
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 animate-pulse rounded-full bg-muted" />
        <div className="space-y-2">
          <div className="h-3 w-32 animate-pulse rounded bg-muted" />
          <div className="h-2 w-24 animate-pulse rounded bg-muted" />
        </div>
      </div>
      <div className="mt-8 h-16 w-48 animate-pulse rounded-xl bg-muted" />
      <div className="mt-6 grid grid-cols-3 gap-3">
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-20 animate-pulse rounded-2xl bg-muted" />
        ))}
      </div>
      <div className="mt-6 h-24 animate-pulse rounded-2xl bg-muted" />
      <p className="mt-4 text-center text-sm text-muted-foreground">
        Menarik data cuaca & tanah, menjalankan model ML...
      </p>
    </div>
  );
}

function ResultCard({ pred }: { pred: Prediction }) {
  const conf = STATUS_CONF[pred.status];
  const total = (pred.yield * pred.area).toFixed(1);

  return (
    <div className="rounded-3xl border border-border/60 bg-[image:var(--gradient-card)] p-8 shadow-[var(--shadow-elegant)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-4 w-4 text-primary" /> {pred.location}
          </div>
          <div className="mt-1 text-xs text-muted-foreground capitalize">
            {pred.crop} · {pred.area} ha · {pred.date}
          </div>
        </div>
        <span
          className={`rounded-full px-3 py-1.5 text-xs font-bold ring-1 ${conf.bg} ${conf.color} ${conf.ring}`}
        >
          {conf.label}
        </span>
      </div>

      {/* Angka utama */}
      <div className="mt-8 flex items-end gap-6">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Estimasi Hasil
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-6xl font-extrabold tracking-tight">{pred.yield}</span>
            <span className="text-xl font-semibold text-muted-foreground">ton/ha</span>
          </div>
        </div>
        <div className="ml-auto rounded-2xl bg-muted/60 px-4 py-3 text-right">
          <div className="text-xs text-muted-foreground">Total panen</div>
          <div className="text-xl font-bold">~{total} ton</div>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-[image:var(--gradient-hero)]"
            style={{ width: `${pred.confidence}%` }}
          />
        </div>
        <span className="font-semibold text-foreground">{pred.confidence}%</span>
        <span>confidence</span>
      </div>

      {/* 3 kartu ringkasan */}
      <div className="mt-6 grid grid-cols-3 gap-3">
        {[
          { i: CloudSun, l: "Cuaca", v: "Otomatis" },
          { i: TrendingUp, l: "Tren Pasar", v: "Diprediksi" },
          { i: Brain, l: "AI Insight", v: "Aktif" },
        ].map((s) => (
          <div key={s.l} className="rounded-2xl bg-muted/40 p-3">
            <s.i className="h-4 w-4 text-primary" />
            <div className="mt-2 text-xs text-muted-foreground">{s.l}</div>
            <div className="text-sm font-semibold">{s.v}</div>
          </div>
        ))}
      </div>

      {/* Saran AI */}
      <div className="mt-6 rounded-2xl border border-primary/20 bg-primary/5 p-5">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary">
          <Brain className="h-3.5 w-3.5" /> Saran AI
        </div>
        <p className="mt-3 text-sm leading-relaxed text-foreground/90">{pred.advice}</p>
      </div>
    </div>
  );
}
