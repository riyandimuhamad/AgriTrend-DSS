import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { DashboardShell, STATUS_CONF } from "@/components/dashboard-shell";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  Search,
  Download,
  MapPin,
  Calendar,
  History as HistoryIcon,
  Loader2,
  Sparkles,
  ChevronRight,
} from "lucide-react";
import { fetchHistory, fetchAdvice, type HistoryItem, type AdviceData } from "@/lib/api/predict";

export const Route = createFileRoute("/riwayat")({
  head: () => ({ meta: [{ title: "Riwayat — Agri Trend DSS" }] }),
  component: RiwayatPage,
});

function statusToConf(status: string) {
  return status === "CRITICAL" ? STATUS_CONF.GAGAL : STATUS_CONF.NORMAL;
}

function RiwayatPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<string>("ALL");
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);
  const [dialogAdvice, setDialogAdvice] = useState<AdviceData | null>(null);
  const [adviceLoading, setAdviceLoading] = useState(false);

  useEffect(() => {
    fetchHistory()
      .then((res) => setHistory(res.data))
      .catch(() => {});
  }, []);

  const filtered = useMemo(() => {
    return history.filter((h) => {
      const q = query.toLowerCase();
      const okQ = !q || h.region.toLowerCase().includes(q) || h.crop_type.toLowerCase().includes(q);
      const okS = filter === "ALL" || h.status === filter;
      return okQ && okS;
    });
  }, [history, query, filter]);

  function openDetail(item: HistoryItem) {
    setSelectedItem(item);
    setDialogAdvice(item.advice ?? null);
  }

  async function loadAdvice() {
    if (!selectedItem) return;
    setAdviceLoading(true);
    try {
      const res = await fetchAdvice(selectedItem.prediction_id);
      setDialogAdvice(res.data);
      setHistory((prev) =>
        prev.map((h) =>
          h.prediction_id === selectedItem.prediction_id ? { ...h, advice: res.data } : h,
        ),
      );
    } catch {
      // silently fail — user can retry
    } finally {
      setAdviceLoading(false);
    }
  }

  const exportCSV = () => {
    const rows = [
      ["Tanggal", "Lokasi", "Tanaman", "Hasil (ton/ha)", "Total (ton)", "Status", "Confidence"],
      ...filtered.map((h) => [
        h.timestamp.slice(0, 10),
        h.region,
        h.crop_type,
        h.yield_per_ha.toFixed(2),
        h.yield_total.toFixed(2),
        h.status,
        `${h.confidence}%`,
      ]),
    ];
    const csv = rows
      .map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `riwayat-prediksi-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totals = useMemo(() => {
    const tot = history.reduce((a, h) => a + h.yield_total, 0);
    const avgConf = history.length
      ? Math.round(history.reduce((a, h) => a + h.confidence, 0) / history.length)
      : 0;
    return { tot: tot.toFixed(1), avgConf, count: history.length };
  }, [history]);

  return (
    <DashboardShell>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Riwayat Prediksi</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Lihat dan kelola seluruh prediksi panen yang pernah Anda buat.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={exportCSV}
          disabled={!filtered.length}
          className="rounded-full"
        >
          <Download className="mr-2 h-4 w-4" /> Export CSV
        </Button>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        {[
          { label: "Total Prediksi", value: totals.count },
          { label: "Total Estimasi Panen", value: `${totals.tot} ton` },
          { label: "Rata-rata Confidence", value: `${totals.avgConf}%` },
        ].map((s) => (
          <div key={s.label} className="rounded-2xl border border-border/60 bg-card p-5">
            <div className="text-xs uppercase tracking-wider text-muted-foreground">{s.label}</div>
            <div className="mt-2 text-2xl font-bold">{s.value}</div>
          </div>
        ))}
      </div>

      <div className="rounded-3xl border border-border/60 bg-card p-6 shadow-[var(--shadow-soft)]">
        <div className="mb-5 flex flex-wrap gap-3">
          <div className="relative min-w-[200px] flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cari lokasi atau tanaman..."
              className="h-11 rounded-xl pl-10"
            />
          </div>
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="h-11 w-[180px] rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">Semua Status</SelectItem>
              <SelectItem value="NORMAL">Normal</SelectItem>
              <SelectItem value="CRITICAL">Gagal</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
              <HistoryIcon className="h-7 w-7 text-primary" />
            </div>
            <h3 className="mt-4 text-base font-semibold">Belum ada riwayat</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Buat prediksi pertama Anda di Dashboard.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-border/60">
            <table className="min-w-[640px] w-full text-sm">
              <thead className="bg-muted/50 text-left text-xs uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-4 py-3">Tanggal</th>
                  <th className="px-4 py-3">Lokasi & Tanaman</th>
                  <th className="px-4 py-3 text-right">Hasil</th>
                  <th className="px-4 py-3 text-right">Total</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Confidence</th>
                  <th className="px-4 py-3 w-8" />
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filtered.map((h) => {
                  const conf = statusToConf(h.status);
                  return (
                    <tr
                      key={h.prediction_id}
                      onClick={() => openDetail(h)}
                      className="cursor-pointer bg-card hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-4 py-3 text-muted-foreground">
                        <Calendar className="mr-1 inline h-3.5 w-3.5" />
                        {h.timestamp.slice(0, 10)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium capitalize">{h.crop_type}</div>
                        <div className="text-xs text-muted-foreground">
                          <MapPin className="mr-1 inline h-3 w-3" />
                          {h.region}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right font-semibold">
                        {h.yield_per_ha.toFixed(2)}{" "}
                        <span className="text-xs text-muted-foreground">t/ha</span>
                      </td>
                      <td className="px-4 py-3 text-right font-bold">
                        {h.yield_total.toFixed(1)} t
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${conf.bg} ${conf.color}`}
                        >
                          {conf.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-muted-foreground">
                        {h.confidence}%
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        <ChevronRight className="h-4 w-4" />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Dialog */}
      <Dialog open={!!selectedItem} onOpenChange={(open) => !open && setSelectedItem(null)}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl">
          {selectedItem && (
            <>
              <DialogHeader>
                <DialogTitle className="text-xl">Detail Prediksi</DialogTitle>
              </DialogHeader>

              {/* Header info */}
              <div className="flex items-center gap-3 rounded-xl bg-muted/50 p-4">
                <div className="flex-1">
                  <div className="text-lg font-bold capitalize">{selectedItem.crop_type}</div>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <MapPin className="h-3.5 w-3.5" />
                    {selectedItem.region}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
                    <Calendar className="h-3 w-3" />
                    {selectedItem.timestamp.slice(0, 10)}
                  </div>
                </div>
                <span
                  className={`rounded-full px-3 py-1.5 text-xs font-semibold ${statusToConf(selectedItem.status).bg} ${statusToConf(selectedItem.status).color}`}
                >
                  {statusToConf(selectedItem.status).label}
                </span>
              </div>

              {/* Metrics grid */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {[
                  { label: "Hasil per Ha", value: `${selectedItem.yield_per_ha.toFixed(2)} t/ha` },
                  { label: "Total Panen", value: `${selectedItem.yield_total.toFixed(1)} ton` },
                  {
                    label: "Rentang Prediksi",
                    value: `${selectedItem.yield_min.toFixed(1)}–${selectedItem.yield_max.toFixed(1)} t/ha`,
                  },
                  { label: "Confidence", value: `${selectedItem.confidence}%` },
                ].map((m) => (
                  <div key={m.label} className="rounded-xl border border-border/60 bg-card p-3">
                    <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
                      {m.label}
                    </div>
                    <div className="mt-1 text-base font-bold">{m.value}</div>
                  </div>
                ))}
              </div>

              {/* AI Advice */}
              <div className="rounded-xl border border-border/60 bg-card p-4">
                <div className="mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  <span className="text-sm font-semibold">Analisis AI</span>
                </div>

                {dialogAdvice ? (
                  <div className="space-y-4">
                    <div>
                      <div className="mb-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">
                        Analisis Pasar
                      </div>
                      <p className="text-sm leading-relaxed text-foreground/90">
                        {dialogAdvice.analysis}
                      </p>
                    </div>
                    <div className="rounded-lg bg-primary/5 border border-primary/20 p-3">
                      <div className="mb-1 text-xs font-medium uppercase tracking-wider text-primary">
                        Rekomendasi
                      </div>
                      <p className="text-sm leading-relaxed font-medium">
                        {dialogAdvice.recommendation}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-3 py-4 text-center">
                    <p className="text-sm text-muted-foreground">
                      Belum ada analisis AI untuk prediksi ini.
                    </p>
                    <Button
                      onClick={loadAdvice}
                      disabled={adviceLoading}
                      size="sm"
                      className="rounded-full"
                    >
                      {adviceLoading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Sparkles className="mr-2 h-4 w-4" />
                      )}
                      {adviceLoading ? "Memuat..." : "Muat Analisis AI"}
                    </Button>
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </DashboardShell>
  );
}
