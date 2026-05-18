import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { DashboardShell, STATUS_CONF, type Prediction } from "@/components/dashboard-shell";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Search, Download, MapPin, Calendar, Trash2, History as HistoryIcon } from "lucide-react";

export const Route = createFileRoute("/riwayat")({
  head: () => ({ meta: [{ title: "Riwayat — Agri Trend DSS" }] }),
  component: RiwayatPage,
});

function RiwayatPage() {
  const [history, setHistory] = useState<Prediction[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<string>("ALL");

  useEffect(() => {
    if (typeof window !== "undefined") {
      const h = localStorage.getItem("sai_history");
      if (h) setHistory(JSON.parse(h));
    }
  }, []);

  const filtered = useMemo(() => {
    return history.filter((h) => {
      const q = query.toLowerCase();
      const okQ = !q || h.location.toLowerCase().includes(q) || h.crop.toLowerCase().includes(q);
      const okS = filter === "ALL" || h.status === filter;
      return okQ && okS;
    });
  }, [history, query, filter]);

  const exportCSV = () => {
    const rows = [
      [
        "Tanggal",
        "Lokasi",
        "Tanaman",
        "Luas (ha)",
        "Hasil (ton/ha)",
        "Total (ton)",
        "Status",
        "Confidence",
      ],
      ...filtered.map((h) => [
        h.date,
        h.location,
        h.crop,
        h.area,
        h.yield,
        (h.yield * h.area).toFixed(2),
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

  const clearAll = () => {
    if (confirm("Hapus semua riwayat prediksi?")) {
      localStorage.removeItem("sai_history");
      setHistory([]);
    }
  };

  const totals = useMemo(() => {
    const tot = history.reduce((a, h) => a + h.yield * h.area, 0);
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
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={exportCSV}
            disabled={!filtered.length}
            className="rounded-full"
          >
            <Download className="mr-2 h-4 w-4" /> Export CSV
          </Button>
          <Button
            variant="outline"
            onClick={clearAll}
            disabled={!history.length}
            className="rounded-full text-destructive hover:text-destructive"
          >
            <Trash2 className="mr-2 h-4 w-4" /> Hapus
          </Button>
        </div>
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
          <div className="relative flex-1 min-w-[200px]">
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
              <SelectItem value="BERLIMPAH">Berlimpah</SelectItem>
              <SelectItem value="NORMAL">Normal</SelectItem>
              <SelectItem value="GAGAL">Gagal</SelectItem>
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
          <div className="overflow-hidden rounded-2xl border border-border/60">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left text-xs uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-4 py-3">Tanggal</th>
                  <th className="px-4 py-3">Lokasi & Tanaman</th>
                  <th className="px-4 py-3 text-right">Luas</th>
                  <th className="px-4 py-3 text-right">Hasil</th>
                  <th className="px-4 py-3 text-right">Total</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {filtered.map((h) => {
                  const conf = STATUS_CONF[h.status];
                  return (
                    <tr key={h.id} className="bg-card hover:bg-muted/30">
                      <td className="px-4 py-3 text-muted-foreground">
                        <Calendar className="mr-1 inline h-3.5 w-3.5" />
                        {h.date}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium capitalize">{h.crop}</div>
                        <div className="text-xs text-muted-foreground">
                          <MapPin className="mr-1 inline h-3 w-3" />
                          {h.location}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">{h.area} ha</td>
                      <td className="px-4 py-3 text-right font-semibold">
                        {h.yield} <span className="text-xs text-muted-foreground">t/ha</span>
                      </td>
                      <td className="px-4 py-3 text-right font-bold">
                        {(h.yield * h.area).toFixed(1)} t
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
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardShell>
  );
}
