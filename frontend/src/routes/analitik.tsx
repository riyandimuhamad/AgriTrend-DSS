import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { DashboardShell } from "@/components/dashboard-shell";
import { TrendingUp, TrendingDown, Sparkles, Leaf, AlertTriangle, BarChart3 } from "lucide-react";
import { fetchHistory, type HistoryItem } from "@/lib/api/predict";

export const Route = createFileRoute("/analitik")({
  head: () => ({ meta: [{ title: "Analitik — Agri Trend DSS" }] }),
  component: AnalitikPage,
});

function AnalitikPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetchHistory()
      .then((res) => setHistory(res.data))
      .catch(() => {});
  }, []);

  const stats = useMemo(() => {
    const total = history.length;
    const totalTon = history.reduce((a, h) => a + h.yield_total, 0);
    const avgYield = total ? history.reduce((a, h) => a + h.yield_per_ha, 0) / total : 0;
    const avgConf = total ? history.reduce((a, h) => a + h.confidence, 0) / total : 0;

    const byCrop: Record<string, { count: number; ton: number }> = {};
    history.forEach((h) => {
      byCrop[h.crop_type] = byCrop[h.crop_type] || { count: 0, ton: 0 };
      byCrop[h.crop_type].count++;
      byCrop[h.crop_type].ton += h.yield_total;
    });

    const byStatus = { NORMAL: 0, CRITICAL: 0 };
    history.forEach((h) => {
      if (h.status === "CRITICAL") byStatus.CRITICAL++;
      else byStatus.NORMAL++;
    });

    const sorted = [...history].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
    const trendPoints = sorted.slice(-12).map((h) => h.yield_per_ha);
    const trendDelta =
      trendPoints.length >= 2
        ? ((trendPoints[trendPoints.length - 1] - trendPoints[0]) / trendPoints[0]) * 100
        : 0;

    return { total, totalTon, avgYield, avgConf, byCrop, byStatus, trendPoints, trendDelta };
  }, [history]);

  const maxTrend = Math.max(1, ...stats.trendPoints);
  const maxCrop = Math.max(1, ...Object.values(stats.byCrop).map((c) => c.ton));

  if (!history.length) {
    return (
      <DashboardShell>
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Analitik</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Insight performa hasil prediksi panen Anda.
          </p>
        </div>
        <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-border bg-card py-20 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
            <BarChart3 className="h-8 w-8 text-primary" />
          </div>
          <h3 className="mt-5 text-lg font-semibold">Belum ada data analitik</h3>
          <p className="mt-2 max-w-sm text-sm text-muted-foreground">
            Buat minimal satu prediksi di Dashboard untuk melihat insight Anda di sini.
          </p>
        </div>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Analitik</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Insight performa hasil prediksi panen Anda.
        </p>
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Total Prediksi", value: stats.total, icon: Sparkles, sub: "model dijalankan" },
          {
            label: "Total Estimasi Panen",
            value: `${stats.totalTon.toFixed(1)} t`,
            icon: Leaf,
            sub: `${stats.total} sesi prediksi`,
          },
          {
            label: "Rata-rata Yield",
            value: `${stats.avgYield.toFixed(2)}`,
            icon: TrendingUp,
            sub: "ton/ha",
          },
          {
            label: "Rata-rata Confidence",
            value: `${stats.avgConf.toFixed(0)}%`,
            icon: AlertTriangle,
            sub: "akurasi model",
          },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-2xl border border-border/60 bg-[image:var(--gradient-card)] p-5 shadow-[var(--shadow-soft)]"
          >
            <div className="flex items-center justify-between">
              <div className="text-xs uppercase tracking-wider text-muted-foreground">
                {s.label}
              </div>
              <s.icon className="h-4 w-4 text-primary" />
            </div>
            <div className="mt-3 text-2xl font-bold">{s.value}</div>
            <div className="mt-1 text-xs text-muted-foreground">{s.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Trend chart */}
        <div className="rounded-3xl border border-border/60 bg-card p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold">Tren Yield (12 prediksi terakhir)</h3>
              <p className="text-xs text-muted-foreground">
                Perbandingan estimasi hasil panen dari waktu ke waktu
              </p>
            </div>
            <div
              className={`flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold ${stats.trendDelta >= 0 ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"}`}
            >
              {stats.trendDelta >= 0 ? (
                <TrendingUp className="h-3.5 w-3.5" />
              ) : (
                <TrendingDown className="h-3.5 w-3.5" />
              )}
              {stats.trendDelta >= 0 ? "+" : ""}
              {stats.trendDelta.toFixed(1)}%
            </div>
          </div>
          {(() => {
            const W = 560,
              H = 160;
            const pad = { t: 24, r: 12, b: 20, l: 12 };
            const iW = W - pad.l - pad.r;
            const iH = H - pad.t - pad.b;
            const pts = stats.trendPoints.map((v, i) => ({
              x:
                pad.l +
                (stats.trendPoints.length > 1 ? (i / (stats.trendPoints.length - 1)) * iW : iW / 2),
              y: pad.t + iH - (v / maxTrend) * iH,
              v,
            }));
            const linePath = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x},${p.y}`).join(" ");
            const areaPath = `${linePath} L${pts[pts.length - 1].x},${pad.t + iH} L${pts[0].x},${pad.t + iH} Z`;
            return (
              <svg viewBox={`0 0 ${W} ${H}`} className="mt-6 w-full" style={{ height: 192 }}>
                <defs>
                  <linearGradient id="lg-trend-line" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="hsl(var(--primary))" />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0.7" />
                  </linearGradient>
                  <linearGradient id="lg-trend-area" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.18" />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d={areaPath} fill="url(#lg-trend-area)" />
                <path
                  d={linePath}
                  fill="none"
                  stroke="url(#lg-trend-line)"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                {pts.map((p, i) => (
                  <g key={i}>
                    <circle cx={p.x} cy={p.y} r="4" fill="hsl(var(--primary))" />
                    <text
                      x={p.x}
                      y={p.y - 9}
                      textAnchor="middle"
                      fontSize="9"
                      fill="hsl(var(--muted-foreground))"
                    >
                      {p.v.toFixed(1)}
                    </text>
                  </g>
                ))}
              </svg>
            );
          })()}
        </div>

        {/* Status breakdown */}
        <div className="rounded-3xl border border-border/60 bg-card p-6">
          <h3 className="text-base font-semibold">Distribusi Status</h3>
          <p className="text-xs text-muted-foreground">Klasifikasi hasil prediksi</p>
          <div className="mt-6 space-y-4">
            {[
              { key: "NORMAL" as const, label: "Normal", color: "bg-primary" },
              { key: "CRITICAL" as const, label: "Gagal Panen", color: "bg-destructive" },
            ].map((s) => {
              const count = stats.byStatus[s.key];
              const pct = stats.total ? (count / stats.total) * 100 : 0;
              return (
                <div key={s.key}>
                  <div className="mb-1.5 flex items-center justify-between text-sm">
                    <span className="font-medium">{s.label}</span>
                    <span className="text-muted-foreground">
                      {count} · {pct.toFixed(0)}%
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className={`h-full rounded-full ${s.color}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Per-crop performance */}
        <div className="rounded-3xl border border-border/60 bg-card p-6 lg:col-span-3">
          <h3 className="text-base font-semibold">Performa per Tanaman</h3>
          <p className="text-xs text-muted-foreground">
            Total estimasi hasil panen berdasarkan jenis tanaman
          </p>
          <div className="mt-6 space-y-4">
            {Object.entries(stats.byCrop).map(([crop, data]) => (
              <div key={crop}>
                <div className="mb-1.5 flex items-center justify-between text-sm">
                  <span className="font-medium capitalize">
                    {crop}{" "}
                    <span className="text-xs text-muted-foreground">({data.count} prediksi)</span>
                  </span>
                  <span className="font-bold">{data.ton.toFixed(1)} ton</span>
                </div>
                <div className="h-3 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-[image:var(--gradient-hero)]"
                    style={{ width: `${(data.ton / maxCrop) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardShell>
  );
}
