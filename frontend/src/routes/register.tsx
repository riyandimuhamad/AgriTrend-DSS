import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { Sprout, ArrowRight, Brain, CloudSun, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState, useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import apiClient from "@/lib/api-client";
import { saveAuth } from "@/lib/auth";

export const Route = createFileRoute("/register")({
  head: () => ({ meta: [{ title: "Daftar — Agri Trend DSS" }] }),
  component: Register,
});

function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Refs for Left Panel
  const logoRef = useRef<HTMLAnchorElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const subtextRef = useRef<HTMLParagraphElement>(null);
  const cardsRef = useRef<HTMLDivElement>(null);
  const copyrightRef = useRef<HTMLDivElement>(null);
  const featureCardRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Refs for Right Panel
  const formHeadingRef = useRef<HTMLHeadingElement>(null);
  const formSubtextRef = useRef<HTMLParagraphElement>(null);
  const fieldRefs = useRef<(HTMLDivElement | null)[]>([]);
  const submitRef = useRef<HTMLButtonElement>(null);
  const footerTextRef = useRef<HTMLParagraphElement>(null);
  const mobileLogoRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      gsap.set(
        [
          logoRef.current,
          headingRef.current,
          subtextRef.current,
          cardsRef.current,
          copyrightRef.current,
          formHeadingRef.current,
          formSubtextRef.current,
          fieldRefs.current,
          submitRef.current,
          footerTextRef.current,
          mobileLogoRef.current,
        ],
        { opacity: 1 },
      );
      return;
    }

    const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

    // Initial state via gsap.set
    gsap.set(logoRef.current, { x: -20 });
    gsap.set(headingRef.current, { y: 40 });
    gsap.set(subtextRef.current, { y: 30 });
    gsap.set(cardsRef.current, { y: 25 });
    gsap.set(formHeadingRef.current, { y: 30 });
    gsap.set(formSubtextRef.current, { y: 20 });
    gsap.set(fieldRefs.current, { y: 20 });
    gsap.set(submitRef.current, { y: 15 });
    gsap.set(mobileLogoRef.current, { x: -16 });

    tl.to(logoRef.current, { opacity: 1, x: 0, duration: 0.5 }, 0.1)
      .to(mobileLogoRef.current, { opacity: 1, x: 0, duration: 0.4 }, 0.1)
      .to(headingRef.current, { opacity: 1, y: 0, duration: 0.7 }, 0.25)
      .to(subtextRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.4)
      .to(cardsRef.current, { opacity: 1, y: 0, duration: 0.5 }, 0.55)
      .to(copyrightRef.current, { opacity: 1, duration: 0.4 }, 0.7)
      // Right Panel overlapping
      .to(formHeadingRef.current, { opacity: 1, y: 0, duration: 0.6 }, 0.2)
      .to(formSubtextRef.current, { opacity: 1, y: 0, duration: 0.5 }, 0.32)
      .to(fieldRefs.current, { opacity: 1, y: 0, duration: 0.45, stagger: 0.1 }, 0.42)
      .to(submitRef.current, { opacity: 1, y: 0, duration: 0.4 }, 0.72)
      .to(footerTextRef.current, { opacity: 1, duration: 0.35 }, 0.88);
  });

  const onMouseEnterFeature = (i: number) => {
    gsap.to(featureCardRefs.current[i], { scale: 1.04, duration: 0.2, ease: "power2.out" });
  };

  const onMouseLeaveFeature = (i: number) => {
    gsap.to(featureCardRefs.current[i], { scale: 1, duration: 0.25, ease: "power2.inOut" });
  };

  const onSubmit = async (e: { preventDefault(): void }) => {
    e.preventDefault();
    setErrorMsg(null);

    if (password !== confirmPassword) {
      setErrorMsg("Kata sandi dan konfirmasi kata sandi tidak cocok.");
      return;
    }

    setLoading(true);

    gsap.to(submitRef.current, {
      scale: 0.97,
      duration: 0.15,
      ease: "power2.in",
      yoyo: true,
      repeat: 1,
    });

    try {
      const res = await apiClient.post<{
        access_token: string | null;
        user: { email: string; user_metadata?: { full_name?: string; name?: string } } | null;
        message: string;
      }>("/api/v1/auth/register", { email, password });

      const { access_token, user } = res.data;

      if (!access_token) {
        setErrorMsg(
          res.data.message || "Pendaftaran berhasil! Silakan cek email Anda untuk verifikasi akun.",
        );
        setLoading(false);
        return;
      }

      saveAuth({ email: user?.email ?? email, name, token: access_token });
      navigate({ to: "/dashboard" });
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 400 || status === 422) {
        setErrorMsg((err as Error)?.message || "Data pendaftaran tidak valid.");
      } else if ((err as Error)?.message) {
        setErrorMsg((err as Error).message);
      } else {
        setErrorMsg("Tidak dapat terhubung ke server. Periksa koneksi Anda.");
      }
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="relative hidden overflow-hidden bg-[image:var(--gradient-hero)] p-12 text-primary-foreground lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-20 -top-20 h-96 w-96 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-32 -left-20 h-96 w-96 rounded-full bg-white/10 blur-3xl" />

        <Link
          ref={logoRef}
          style={{ opacity: 0 }}
          to="/"
          className="relative flex items-center gap-2"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/20 backdrop-blur">
            <Sprout className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold">Agri Trend DSS</span>
        </Link>

        <div className="relative">
          <h2 ref={headingRef} style={{ opacity: 0 }} className="text-4xl font-bold leading-tight">
            Mulai perjalanan tani cerdasmu hari ini.
          </h2>
          <p ref={subtextRef} style={{ opacity: 0 }} className="mt-4 text-primary-foreground/80">
            Daftar gratis dan dapatkan prediksi panen pertama Anda dalam hitungan detik.
          </p>
          <div ref={cardsRef} style={{ opacity: 0 }} className="mt-8 grid grid-cols-3 gap-4">
            {[
              { i: Brain, l: "AI Insights" },
              { i: CloudSun, l: "Data Cuaca" },
              { i: BarChart3, l: "Analitik" },
            ].map((x, i) => (
              <div
                key={x.l}
                ref={(el) => {
                  featureCardRefs.current[i] = el;
                }}
                onMouseEnter={() => onMouseEnterFeature(i)}
                onMouseLeave={() => onMouseLeaveFeature(i)}
                className="rounded-2xl bg-white/10 p-4 backdrop-blur transition-colors hover:bg-white/15"
              >
                <x.i className="h-5 w-5" />
                <div className="mt-2 text-sm font-medium">{x.l}</div>
              </div>
            ))}
          </div>
        </div>

        <div
          ref={copyrightRef}
          style={{ opacity: 0 }}
          className="relative text-xs text-primary-foreground/70"
        >
          © 2025 Capstone Project
        </div>
      </div>

      <div className="flex flex-col justify-center px-6 py-12 sm:px-12 lg:px-16">
        <div ref={mobileLogoRef} style={{ opacity: 0 }} className="lg:hidden mb-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[image:var(--gradient-hero)]">
              <Sprout className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-lg font-bold">Agri Trend DSS</span>
          </Link>
        </div>

        <div className="mx-auto w-full max-w-md">
          <h1
            ref={formHeadingRef}
            style={{ opacity: 0 }}
            className="text-3xl font-bold tracking-tight"
          >
            Buat akun baru
          </h1>
          <p
            ref={formSubtextRef}
            style={{ opacity: 0 }}
            className="mt-2 text-sm text-muted-foreground"
          >
            Isi data di bawah untuk mulai menggunakan Agri Trend DSS.
          </p>

          <form onSubmit={onSubmit} className="mt-8 space-y-5">
            <div
              ref={(el) => {
                fieldRefs.current[0] = el;
              }}
              style={{ opacity: 0 }}
              className="space-y-2"
            >
              <Label htmlFor="name">Nama Lengkap</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Contoh: Budi Santoso"
                required
                className="h-12 rounded-xl"
              />
            </div>
            <div
              ref={(el) => {
                fieldRefs.current[1] = el;
              }}
              style={{ opacity: 0 }}
              className="space-y-2"
            >
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-12 rounded-xl"
              />
            </div>
            <div
              ref={(el) => {
                fieldRefs.current[2] = el;
              }}
              style={{ opacity: 0 }}
              className="space-y-2"
            >
              <Label htmlFor="password">Kata Sandi</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="h-12 rounded-xl"
              />
            </div>
            <div
              ref={(el) => {
                fieldRefs.current[3] = el;
              }}
              style={{ opacity: 0 }}
              className="space-y-2"
            >
              <Label htmlFor="confirm-password">Konfirmasi Kata Sandi</Label>
              <Input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="h-12 rounded-xl"
              />
            </div>

            {errorMsg && (
              <p className="rounded-xl bg-destructive/10 px-4 py-2.5 text-sm text-destructive">
                {errorMsg}
              </p>
            )}

            <Button
              ref={submitRef}
              style={{ opacity: 0 }}
              type="submit"
              disabled={loading}
              className="h-12 w-full rounded-xl bg-[image:var(--gradient-hero)] text-base font-semibold shadow-[var(--shadow-elegant)] hover:opacity-95"
            >
              {loading ? (
                "Memuat..."
              ) : (
                <>
                  Buat Akun <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </form>

          <p
            ref={footerTextRef}
            style={{ opacity: 0 }}
            className="mt-8 text-center text-sm text-muted-foreground"
          >
            Sudah punya akun?{" "}
            <Link to="/login" className="font-semibold text-primary hover:underline">
              Masuk di sini
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
