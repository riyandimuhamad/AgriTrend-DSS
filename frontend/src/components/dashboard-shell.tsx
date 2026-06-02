import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { Sprout, LogOut, History, TrendingUp, Leaf, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState, type ReactNode } from "react";
import { clearAuth, getUser } from "@/lib/auth";

const NAV = [
  { icon: Home, label: "Dashboard", to: "/dashboard" as const },
  { icon: History, label: "Riwayat", to: "/riwayat" as const },
  { icon: TrendingUp, label: "Analitik", to: "/analitik" as const },
  { icon: Leaf, label: "Lahan Saya", to: "/lahan" as const },
];

export function DashboardShell({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [user, setUser] = useState<{ email: string; name: string } | null>(null);

  useEffect(() => {
    const u = getUser();
    if (!u) {
      navigate({ to: "/login" });
      return;
    }
    setUser(u);
  }, [navigate]);

  const logout = () => {
    clearAuth();
    navigate({ to: "/" });
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-muted/30">
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-border/60 bg-sidebar lg:flex">
        <div className="flex h-16 items-center gap-2 border-b border-sidebar-border px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[image:var(--gradient-hero)]">
            <Sprout className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-base font-bold">Agri Trend DSS</span>
        </div>
        <nav className="flex-1 space-y-1 p-4">
          {NAV.map((item) => {
            const active = pathname === item.to;
            return (
              <Link
                key={item.label}
                to={item.to}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${active ? "bg-sidebar-primary text-sidebar-primary-foreground" : "text-sidebar-foreground hover:bg-sidebar-accent"}`}
              >
                <item.icon className="h-4 w-4" /> {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-sidebar-border p-4">
          <div className="flex items-center gap-3 rounded-xl bg-sidebar-accent p-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[image:var(--gradient-hero)] text-sm font-bold text-primary-foreground">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-semibold">{user.name}</div>
              <div className="truncate text-xs text-muted-foreground">{user.email}</div>
            </div>
            <button
              onClick={logout}
              className="rounded-lg p-2 text-muted-foreground hover:bg-background hover:text-foreground"
              aria-label="Keluar"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border/60 bg-background/80 px-6 backdrop-blur lg:px-10">
          <div>
            <div className="text-xs text-muted-foreground">Selamat datang kembali,</div>
            <div className="text-sm font-semibold capitalize">{user.name}</div>
          </div>
          <div className="flex items-center gap-2 overflow-x-auto lg:hidden">
            {NAV.map((item) => {
              const active = pathname === item.to;
              return (
                <Link
                  key={item.label}
                  to={item.to}
                  className={`rounded-full px-3 py-1.5 text-xs font-medium ${active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
          <div className="hidden items-center gap-2 lg:flex">
            <Button asChild variant="outline" size="sm" className="rounded-full">
              <Link to="/">Beranda</Link>
            </Button>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8 lg:px-10">{children}</main>
      </div>
    </div>
  );
}

export type Prediction = {
  id: string;
  location: string;
  crop: string;
  area: number;
  date: string;
  plantingDate: string;
  yield: number;
  yieldTotal: number;
  status: "BERLIMPAH" | "NORMAL" | "GAGAL";
  confidence: number;
  advice: string;
};

export const STATUS_CONF = {
  BERLIMPAH: {
    label: "Panen Berlimpah",
    color: "text-success",
    bg: "bg-success/10",
    ring: "ring-success/20",
  },
  NORMAL: { label: "Normal", color: "text-primary", bg: "bg-primary/10", ring: "ring-primary/20" },
  GAGAL: {
    label: "Risiko Gagal",
    color: "text-destructive",
    bg: "bg-destructive/10",
    ring: "ring-destructive/20",
  },
};
