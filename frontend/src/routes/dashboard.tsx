import { createFileRoute } from "@tanstack/react-router";
import {
  Sparkles,
  Brain,
  CloudSun,
  Leaf,
  MapPin,
  TrendingUp,
  Droplets,
  Thermometer,
  FlaskConical,
} from "lucide-react";
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

function Dashboard() {
  const [history, setHistory] = useState<Prediction[]>([]);
  const [current, setCurrent] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // form state — sesuai PredictionRequest schema backend
  const [nitrogen, setNitrogen] = useState("50");
  const [phosphorus, setPhosphorus] = useState("30");
  const [potassium, setPotassium] = useState("40");
  const [temperature, setTemperature] = useState("28");
  const [humidity, setHumidity] = useState("76");
  const [ph, setPh] = useState("6.5");
  const [rainfall, setRainfall] = useState("200");
  const [cropType, setCropType] = useState("padi");
  const [location, setLocation] = useState("");
  const [area, setArea] = useState("2.5");
  const [insightMode, setInsightMode] = useState<"market_only" | "agronomy_plus_market">(
    "agronomy_plus_market",
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
        nitrogen: parseFloat(nitrogen),
        phosphorus: parseFloat(phosphorus),
        potassium: parseFloat(potassium),
        temperature: parseFloat(temperature),
        humidity: parseFloat(humidity),
        ph: parseFloat(ph),
        rainfall: parseFloat(rainfall),
        crop_type: cropType,
        nama_kabupaten_kota: location.trim() || null,
        insight_mode: insightMode,
      });

      const yieldVal = data.prediction.predicted_yield_ton_per_ha;
      const status = marketTrendToStatus(data.prediction.market_trend);
      const advice = extractAdvice(data.insight_structured, data.insight);
      const region = data.prediction.coordinates?.region ?? location.trim() ?? "Tidak diketahui";

      const pred: Prediction = {
        id: crypto.randomUUID(),
        location: region,
        crop: cropType,
        area: parseFloat(area),
        date: new Date().toISOString().slice(0, 10),
        yield: parseFloat(yieldVal.toFixed(2)),
        status,
        confidence: 85,
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
          Masukkan data lahan dan kondisi lingkungan — model ML akan menghitung estimasi panen Anda.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Form */}
        <div className="lg:col-span-2">
          <form
            onSubmit={onSubmit}
            className="rounded-3xl border border-border/60 bg-card p-6 shadow-[var(--shadow-soft)]"
          >
            <h2 className="text-lg font-semibold">Data Lahan & Lingkungan</h2>

            {/* Jenis tanaman + lokasi */}
            <div className="mt-5 space-y-4">
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
                    <SelectItem value="kedelai">Kedelai</SelectItem>
                    <SelectItem value="cabai">Cabai</SelectItem>
                    <SelectItem value="kopi">Kopi</SelectItem>
                    <SelectItem value="tebu">Tebu</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="loc">
                  <MapPin className="mr-1 inline h-3.5 w-3.5" />
                  Lokasi (Opsional)
                </Label>
                <Input
                  id="loc"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Contoh: Sleman"
                  className="h-11 rounded-xl"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="area">Luas Lahan (ha)</Label>
                <Input
                  id="area"
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                  required
                  className="h-11 rounded-xl"
                />
              </div>
            </div>

            {/* Nutrisi tanah */}
            <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Nutrisi Tanah (mg/kg)
            </p>
            <div className="mt-2 grid grid-cols-3 gap-3">
              {[
                { id: "n", label: "N", val: nitrogen, set: setNitrogen },
                { id: "p", label: "P", val: phosphorus, set: setPhosphorus },
                { id: "k", label: "K", val: potassium, set: setPotassium },
              ].map(({ id, label, val, set }) => (
                <div key={id} className="space-y-1.5">
                  <Label htmlFor={id} className="text-xs">
                    {label}
                  </Label>
                  <Input
                    id={id}
                    type="number"
                    step="0.1"
                    min="0"
                    value={val}
                    onChange={(e) => set(e.target.value)}
                    required
                    className="h-10 rounded-xl text-sm"
                  />
                </div>
              ))}
            </div>

            {/* Iklim */}
            <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Kondisi Iklim
            </p>
            <div className="mt-2 grid grid-cols-3 gap-3">
              {[
                { id: "temp", label: "Suhu (°C)", val: temperature, set: setTemperature },
                { id: "hum", label: "Lembab (%)", val: humidity, set: setHumidity },
                { id: "rain", label: "Hujan (mm)", val: rainfall, set: setRainfall },
              ].map(({ id, label, val, set }) => (
                <div key={id} className="space-y-1.5">
                  <Label htmlFor={id} className="text-xs">
                    {label}
                  </Label>
                  <Input
                    id={id}
                    type="number"
                    step="0.1"
                    value={val}
                    onChange={(e) => set(e.target.value)}
                    required
                    className="h-10 rounded-xl text-sm"
                  />
                </div>
              ))}
            </div>

            {/* pH + insight mode */}
            <div className="mt-4 grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="ph">pH Tanah (0–14)</Label>
                <Input
                  id="ph"
                  type="number"
                  step="0.1"
                  min="0"
                  max="14"
                  value={ph}
                  onChange={(e) => setPh(e.target.value)}
                  required
                  className="h-11 rounded-xl"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="insight">Mode Insight</Label>
                <Select
                  value={insightMode}
                  onValueChange={(v) => setInsightMode(v as typeof insightMode)}
                >
                  <SelectTrigger id="insight" className="h-11 rounded-xl">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="agronomy_plus_market">Agronomi + Pasar</SelectItem>
                    <SelectItem value="market_only">Pasar Saja</SelectItem>
                  </SelectContent>
                </Select>
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

          {/* Live data preview */}
          <div className="mt-6 grid grid-cols-3 gap-3">
            {[
              { i: CloudSun, l: "Suhu", v: `${temperature}°C` },
              { i: Droplets, l: "Lembab", v: `${humidity}%` },
              { i: Thermometer, l: "pH Tanah", v: ph },
            ].map((s) => (
              <div key={s.l} className="rounded-2xl border border-border/60 bg-card p-4">
                <s.i className="h-4 w-4 text-primary" />
                <div className="mt-2 text-xs text-muted-foreground">{s.l}</div>
                <div className="text-sm font-semibold">{s.v}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Result */}
        <div className="lg:col-span-3">
          {apiError && (
            <div className="mb-4">
              <ApiError message={apiError} onRetry={() => setApiError(null)} />
            </div>
          )}
          {loading && <SkeletonResult />}
          {!loading && !current && !apiError && <EmptyState />}
          {!loading && current && <ResultCard pred={current} />}

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
        Menarik data cuaca, tanah, & menjalankan model ML...
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

      <div className="mt-6 grid grid-cols-3 gap-3">
        {[
          { i: CloudSun, l: "Cuaca", v: "Optimal" },
          { i: FlaskConical, l: "Nutrisi", v: "Teranalisa" },
          { i: TrendingUp, l: "Tren Pasar", v: "Diprediksi" },
        ].map((s) => (
          <div key={s.l} className="rounded-2xl bg-muted/40 p-3">
            <s.i className="h-4 w-4 text-primary" />
            <div className="mt-2 text-xs text-muted-foreground">{s.l}</div>
            <div className="text-sm font-semibold">{s.v}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-2xl border border-primary/20 bg-primary/5 p-5">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary">
          <Brain className="h-3.5 w-3.5" /> Saran AI
        </div>
        <p className="mt-3 text-sm leading-relaxed text-foreground/90">{pred.advice}</p>
      </div>
    </div>
  );
}
