import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { Sprout, LogOut, History, TrendingUp, Home, Menu } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { clearAuth, getUser } from "@/lib/auth";
import { Sheet, SheetContent, SheetTrigger, SheetClose } from "@/components/ui/sheet";

const NAV = [
  { icon: Home, label: "Dashboard", to: "/dashboard" as const },
  { icon: History, label: "Riwayat", to: "/riwayat" as const },
  { icon: TrendingUp, label: "Analitik", to: "/analitik" as const },
];

function SidebarContent({
  user,
  pathname,
  logout,
  withClose,
}: {
  user: { email: string; name: string };
  pathname: string;
  logout: () => void;
  withClose?: boolean;
}) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center gap-2 border-b border-sidebar-border px-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[image:var(--gradient-hero)]">
          <Sprout className="h-5 w-5 text-primary-foreground" />
        </div>
        <span className="text-base font-bold">Agri Trend DSS</span>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {NAV.map((item) => {
          const active = pathname === item.to;
          const link = (
            <Link
              key={item.label}
              to={item.to}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors ${active ? "bg-sidebar-primary text-sidebar-primary-foreground" : "text-sidebar-foreground hover:bg-sidebar-accent"}`}
            >
              <item.icon className="h-4 w-4" /> {item.label}
            </Link>
          );
          return withClose ? (
            <SheetClose key={item.label} asChild>
              {link}
            </SheetClose>
          ) : (
            link
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
    </div>
  );
}

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
      {/* Desktop Sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-border/60 bg-sidebar lg:flex">
        <SidebarContent user={user} pathname={pathname} logout={logout} />
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border/60 bg-background/80 px-4 backdrop-blur sm:px-6 lg:px-10">
          {/* Mobile: hamburger + logo */}
          <div className="flex items-center gap-3 lg:hidden">
            <Sheet>
              <SheetTrigger asChild>
                <button
                  className="rounded-lg p-2 text-foreground hover:bg-muted"
                  aria-label="Buka menu"
                >
                  <Menu className="h-5 w-5" />
                </button>
              </SheetTrigger>
              <SheetContent side="left" className="w-72 p-0 bg-sidebar">
                <SidebarContent user={user} pathname={pathname} logout={logout} withClose />
              </SheetContent>
            </Sheet>
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[image:var(--gradient-hero)]">
                <Sprout className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="text-sm font-bold">Agri Trend DSS</span>
            </div>
          </div>

          {/* Desktop: welcome text */}
          <div className="hidden lg:block">
            <div className="text-xs text-muted-foreground">Selamat datang kembali,</div>
            <div className="text-sm font-semibold capitalize">{user.name}</div>
          </div>

          {/* Mobile: welcome text (right side) */}
          <div className="lg:hidden">
            <div className="text-xs text-muted-foreground">Halo,</div>
            <div className="text-sm font-semibold capitalize">{user.name}</div>
          </div>
          <div className="hidden items-center gap-2 lg:flex" />
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-10 lg:py-8">{children}</main>
      </div>
    </div>
  );
}

export type Prediction = {
  id: string;
  predictionId: string;
  location: string;
  crop: string;
  area: number;
  date: string;
  plantingDate: string;
  yield: number;
  yieldTotal: number;
  status: "BERLIMPAH" | "NORMAL" | "GAGAL";
  confidence: number;
  advice: { analysis: string; recommendation: string } | null;
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
