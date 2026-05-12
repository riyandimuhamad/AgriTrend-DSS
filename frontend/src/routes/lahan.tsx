import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type FormEvent } from "react";
import { requireAuth } from "@/lib/auth-guard";
import { DashboardShell } from "@/components/dashboard-shell";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Plus, MapPin, Leaf, Droplets, Trash2, Pencil, Sprout } from "lucide-react";

export const Route = createFileRoute("/lahan")({
  head: () => ({ meta: [{ title: "Lahan Saya — Agri Trend DSS" }] }),
  beforeLoad: requireAuth,
  component: LahanPage,
});

type Field = {
  id: string;
  name: string;
  location: string;
  area: number;
  crop: string;
  soil: string;
  irrigation: string;
  plantedAt: string;
};

const DEFAULT_FIELDS: Field[] = [
  {
    id: "f1",
    name: "Sawah Utara",
    location: "Sleman, DI Yogyakarta",
    area: 2.5,
    crop: "padi",
    soil: "Aluvial",
    irrigation: "Teknis",
    plantedAt: "2026-03-15",
  },
  {
    id: "f2",
    name: "Kebun Jagung",
    location: "Magelang, Jawa Tengah",
    area: 1.8,
    crop: "jagung",
    soil: "Latosol",
    irrigation: "Tadah Hujan",
    plantedAt: "2026-04-02",
  },
  {
    id: "f3",
    name: "Lahan Cabai",
    location: "Bantul, DI Yogyakarta",
    area: 0.6,
    crop: "cabai",
    soil: "Regosol",
    irrigation: "Tetes",
    plantedAt: "2026-04-20",
  },
];

const CROP_HEALTH: Record<string, { label: string; color: string; pct: number }> = {
  padi: { label: "Sehat", color: "text-success bg-success/10", pct: 86 },
  jagung: { label: "Perlu Pantau", color: "text-warning bg-warning/10", pct: 64 },
  kedelai: { label: "Sehat", color: "text-success bg-success/10", pct: 78 },
  cabai: { label: "Sehat", color: "text-success bg-success/10", pct: 81 },
};

function LahanPage() {
  const [fields, setFields] = useState<Field[]>([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Field | null>(null);

  useEffect(() => {
    const f = localStorage.getItem("sai_fields");
    if (f) setFields(JSON.parse(f));
    else {
      setFields(DEFAULT_FIELDS);
      localStorage.setItem("sai_fields", JSON.stringify(DEFAULT_FIELDS));
    }
  }, []);

  const persist = (next: Field[]) => {
    setFields(next);
    localStorage.setItem("sai_fields", JSON.stringify(next));
  };

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const data: Field = {
      id: editing?.id ?? crypto.randomUUID(),
      name: String(fd.get("name") || ""),
      location: String(fd.get("location") || ""),
      area: parseFloat(String(fd.get("area") || "0")),
      crop: String(fd.get("crop") || "padi"),
      soil: String(fd.get("soil") || ""),
      irrigation: String(fd.get("irrigation") || "Teknis"),
      plantedAt: String(fd.get("plantedAt") || ""),
    };
    persist(editing ? fields.map((f) => (f.id === editing.id ? data : f)) : [data, ...fields]);
    setOpen(false);
    setEditing(null);
  };

  const remove = (id: string) => {
    if (confirm("Hapus lahan ini?")) persist(fields.filter((f) => f.id !== id));
  };

  const totalHa = fields.reduce((a, f) => a + f.area, 0);

  return (
    <DashboardShell>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Lahan Saya</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Kelola data lahan untuk mempercepat input prediksi.
          </p>
        </div>
        <Dialog
          open={open}
          onOpenChange={(o) => {
            setOpen(o);
            if (!o) setEditing(null);
          }}
        >
          <DialogTrigger asChild>
            <Button
              className="rounded-full bg-[image:var(--gradient-hero)]"
              onClick={() => setEditing(null)}
            >
              <Plus className="mr-2 h-4 w-4" /> Tambah Lahan
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>{editing ? "Ubah Lahan" : "Tambah Lahan Baru"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={onSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nama Lahan</Label>
                <Input
                  id="name"
                  name="name"
                  required
                  defaultValue={editing?.name}
                  placeholder="Sawah Utara"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="location">Lokasi</Label>
                <Input
                  id="location"
                  name="location"
                  required
                  defaultValue={editing?.location}
                  placeholder="Kecamatan, Kabupaten"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="area">Luas (ha)</Label>
                  <Input
                    id="area"
                    name="area"
                    type="number"
                    step="0.1"
                    min="0.1"
                    required
                    defaultValue={editing?.area}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="crop">Tanaman</Label>
                  <Select name="crop" defaultValue={editing?.crop ?? "padi"}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="padi">Padi</SelectItem>
                      <SelectItem value="jagung">Jagung</SelectItem>
                      <SelectItem value="kedelai">Kedelai</SelectItem>
                      <SelectItem value="cabai">Cabai</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="soil">Jenis Tanah</Label>
                  <Input id="soil" name="soil" defaultValue={editing?.soil} placeholder="Aluvial" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="irrigation">Irigasi</Label>
                  <Select name="irrigation" defaultValue={editing?.irrigation ?? "Teknis"}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Teknis">Teknis</SelectItem>
                      <SelectItem value="Setengah Teknis">Setengah Teknis</SelectItem>
                      <SelectItem value="Tadah Hujan">Tadah Hujan</SelectItem>
                      <SelectItem value="Tetes">Tetes</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="plantedAt">Tanggal Tanam</Label>
                <Input
                  id="plantedAt"
                  name="plantedAt"
                  type="date"
                  required
                  defaultValue={editing?.plantedAt}
                />
              </div>
              <DialogFooter>
                <Button type="submit" className="bg-[image:var(--gradient-hero)]">
                  {editing ? "Simpan" : "Tambah"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        {[
          { label: "Total Lahan", value: fields.length },
          { label: "Total Luas", value: `${totalHa.toFixed(1)} ha` },
          { label: "Jenis Tanaman", value: new Set(fields.map((f) => f.crop)).size },
        ].map((s) => (
          <div key={s.label} className="rounded-2xl border border-border/60 bg-card p-5">
            <div className="text-xs uppercase tracking-wider text-muted-foreground">{s.label}</div>
            <div className="mt-2 text-2xl font-bold">{s.value}</div>
          </div>
        ))}
      </div>

      {fields.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-border bg-card py-20 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
            <Sprout className="h-8 w-8 text-primary" />
          </div>
          <h3 className="mt-5 text-lg font-semibold">Belum ada lahan terdaftar</h3>
          <p className="mt-2 max-w-sm text-sm text-muted-foreground">
            Tambahkan lahan pertama Anda untuk mulai mengelola data prediksi.
          </p>
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {fields.map((f) => {
            const health = CROP_HEALTH[f.crop] ?? CROP_HEALTH.padi;
            return (
              <div
                key={f.id}
                className="group overflow-hidden rounded-3xl border border-border/60 bg-card shadow-[var(--shadow-soft)] transition-shadow hover:shadow-[var(--shadow-elegant)]"
              >
                <div className="relative h-28 bg-[image:var(--gradient-hero)] p-4">
                  <div
                    className="absolute inset-0 opacity-30"
                    style={{
                      backgroundImage:
                        "radial-gradient(circle at 80% 20%, rgba(255,255,255,0.3), transparent 60%)",
                    }}
                  />
                  <div className="relative flex items-start justify-between">
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wider text-primary-foreground/80">
                        {f.crop}
                      </div>
                      <div className="text-lg font-bold text-primary-foreground">{f.name}</div>
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${health.color}`}
                    >
                      {health.label}
                    </span>
                  </div>
                </div>
                <div className="p-5">
                  <div className="space-y-2.5 text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <MapPin className="h-4 w-4 text-primary" />
                      {f.location}
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Leaf className="h-4 w-4 text-primary" />
                      {f.area} ha · Tanah {f.soil || "-"}
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Droplets className="h-4 w-4 text-primary" />
                      Irigasi {f.irrigation} · Tanam {f.plantedAt}
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="mb-1.5 flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Indeks Kesehatan Tanaman</span>
                      <span className="font-semibold">{health.pct}%</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-[image:var(--gradient-hero)]"
                        style={{ width: `${health.pct}%` }}
                      />
                    </div>
                  </div>
                  <div className="mt-5 flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 rounded-full"
                      onClick={() => {
                        setEditing(f);
                        setOpen(true);
                      }}
                    >
                      <Pencil className="mr-1.5 h-3.5 w-3.5" /> Ubah
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="rounded-full text-destructive hover:bg-destructive/10 hover:text-destructive"
                      onClick={() => remove(f.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </DashboardShell>
  );
}
