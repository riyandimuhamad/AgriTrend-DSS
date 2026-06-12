import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useRef } from "react";
import {
  Sprout,
  Brain,
  CloudSun,
  BarChart3,
  ArrowRight,
  Check,
  Leaf,
  MapPin,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplashScreen } from "@/components/SplashScreen";

export const Route = createFileRoute("/")({
  component: Landing,
});

function Landing() {
  const [splashDone, setSplashDone] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {!splashDone && <SplashScreen onComplete={() => setSplashDone(true)} />}
      <Header />
      <Hero splashDone={splashDone} />
      <Features />
      <HowItWorks />
      <Stats />
      <CTA />
      <Footer />
    </div>
  );
}

function Header() {
  const headerRef = useRef<HTMLElement>(null);

  useGSAP(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    ScrollTrigger.create({
      start: "top -80",
      onEnter: () => {
        gsap.to(headerRef.current, {
          boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
          backgroundColor: "rgba(255, 255, 255, 0.95)",
          duration: 0.3,
        });
      },
      onLeaveBack: () => {
        gsap.to(headerRef.current, {
          boxShadow: "none",
          backgroundColor: "transparent",
          duration: 0.3,
        });
      },
    });
  });

  return (
    <header
      ref={headerRef}
      className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-lg"
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[image:var(--gradient-hero)] shadow-[var(--shadow-soft)]">
            <Sprout className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-lg font-bold tracking-tight">Agri Trend DSS</span>
        </Link>
        <nav className="hidden items-center gap-8 md:flex">
          <a
            href="#fitur"
            className="text-sm font-medium text-muted-foreground hover:text-foreground"
          >
            Fitur
          </a>
          <a
            href="#cara-kerja"
            className="text-sm font-medium text-muted-foreground hover:text-foreground"
          >
            Cara Kerja
          </a>
          <a
            href="#statistik"
            className="text-sm font-medium text-muted-foreground hover:text-foreground"
          >
            Statistik
          </a>
        </nav>
        <div className="flex items-center gap-3">
          <Button asChild size="sm" className="rounded-full">
            <Link to="/login">Mulai Sekarang</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}

function Hero({ splashDone }: { splashDone: boolean }) {
  const badgeRef = useRef<HTMLDivElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const paraRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const trustRef = useRef<HTMLDivElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const floatingCardRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (!splashDone) return;
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.set(
          [
            badgeRef.current,
            headingRef.current,
            paraRef.current,
            ctaRef.current,
            trustRef.current,
            cardRef.current,
            floatingCardRef.current,
          ],
          { opacity: 1 },
        );
        return;
      }

      const tl = gsap.timeline();

      tl.fromTo(
        badgeRef.current,
        { opacity: 0, y: -16 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" },
      )
        .fromTo(
          headingRef.current,
          { opacity: 0, y: 40 },
          { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" },
          "-=0.3",
        )
        .fromTo(
          paraRef.current,
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" },
          "-=0.4",
        )
        .fromTo(
          ctaRef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" },
          "-=0.3",
        )
        .fromTo(
          trustRef.current,
          { opacity: 0 },
          { opacity: 1, duration: 0.4, ease: "power2.out" },
          "-=0.2",
        )
        .fromTo(
          cardRef.current,
          { opacity: 0, y: 50, scale: 0.96 },
          { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "power3.out" },
          "-=1.5",
        )
        .fromTo(
          floatingCardRef.current,
          { opacity: 0, x: -20, y: 10 },
          { opacity: 1, x: 0, y: 0, duration: 0.5, ease: "back.out(1.4)" },
          "-=0.1",
        );
    },
    { dependencies: [splashDone] },
  );

  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 bg-[image:var(--gradient-soft)]" />
      <div className="absolute -top-24 right-[-10%] h-[480px] w-[480px] rounded-full bg-primary/10 blur-3xl" />
      <div className="absolute -bottom-24 left-[-10%] h-[480px] w-[480px] rounded-full bg-accent/20 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-6 pt-20 pb-24 md:pt-28 md:pb-32">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <div
              ref={badgeRef}
              style={{ opacity: 0 }}
              className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary"
            >
              <Sparkles className="h-3.5 w-3.5" />
              PJK-GM023's Capstone Project 2026
            </div>
            <h1
              ref={headingRef}
              style={{ opacity: 0 }}
              className="mt-6 text-5xl font-extrabold leading-[1.05] tracking-tight md:text-6xl lg:text-7xl"
            >
              Prediksi panen{" "}
              <span className="bg-gradient-to-br from-primary to-primary-glow bg-clip-text text-transparent">
                cerdas
              </span>{" "}
              untuk petani Indonesia.
            </h1>
            <p
              ref={paraRef}
              style={{ opacity: 0 }}
              className="mt-6 max-w-xl text-lg text-muted-foreground"
            >
              Cukup masukkan lokasi dan jenis tanaman. Sistem otomatis menarik data cuaca, tanah,
              dan historis — lalu memberi estimasi hasil panen serta saran bisnis dalam Bahasa
              Indonesia yang mudah dipahami.
            </p>
            <div ref={ctaRef} style={{ opacity: 0 }} className="mt-8 flex flex-wrap gap-3">
              <Button
                asChild
                size="lg"
                className="rounded-full bg-[image:var(--gradient-hero)] shadow-[var(--shadow-elegant)] hover:opacity-95"
              >
                <Link to="/login">
                  Coba Gratis <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="rounded-full">
                <a href="#cara-kerja">Lihat Cara Kerja</a>
              </Button>
            </div>
            <div
              ref={trustRef}
              style={{ opacity: 0 }}
              className="mt-8 flex flex-wrap items-center gap-6 text-sm text-muted-foreground"
            >
              {["Tanpa instalasi", "Bahasa Indonesia", "Data publik resmi"].map((t) => (
                <div key={t} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" /> {t}
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
            <div
              ref={cardRef}
              style={{ opacity: 0 }}
              className="rounded-3xl border border-border/60 bg-[image:var(--gradient-card)] p-6 shadow-[var(--shadow-elegant)]"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <MapPin className="h-4 w-4 text-primary" /> Sleman, DI Yogyakarta
                </div>
                <span className="rounded-full bg-success/10 px-3 py-1 text-xs font-semibold text-success">
                  NORMAL
                </span>
              </div>

              <div className="mt-6">
                <div className="text-sm font-medium text-muted-foreground">
                  Estimasi Hasil Panen
                </div>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-6xl font-extrabold tracking-tight">6.4</span>
                  <span className="text-xl font-semibold text-muted-foreground">ton/ha</span>
                </div>
                <div className="mt-1 text-sm text-muted-foreground">
                  Confidence interval: 5.8 – 7.0 ton/ha · 87% confidence
                </div>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3">
                {[
                  { label: "Cuaca", value: "Optimal", icon: CloudSun },
                  { label: "Tanah", value: "Subur", icon: Leaf },
                  { label: "Tren", value: "+12%", icon: BarChart3 },
                ].map((s) => (
                  <div key={s.label} className="rounded-2xl bg-muted/50 p-3">
                    <s.icon className="h-4 w-4 text-primary" />
                    <div className="mt-2 text-xs text-muted-foreground">{s.label}</div>
                    <div className="text-sm font-semibold">{s.value}</div>
                  </div>
                ))}
              </div>

              <div className="mt-6 rounded-2xl bg-primary/5 p-4">
                <div className="flex items-center gap-2 text-xs font-semibold text-primary">
                  <Brain className="h-3.5 w-3.5" /> SARAN AI
                </div>
                <p className="mt-2 text-sm leading-relaxed text-foreground/80">
                  Prediksi panen sangat baik. Pertimbangkan menghubungi pengepul lebih awal untuk
                  harga terbaik sebelum pasokan melimpah di pasar.
                </p>
              </div>
            </div>
            <div
              ref={floatingCardRef}
              style={{ opacity: 0 }}
              className="absolute -bottom-6 -left-6 hidden rounded-2xl border border-border/60 bg-card p-4 shadow-[var(--shadow-soft)] md:block"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/30">
                  <Sprout className="h-5 w-5 text-accent-foreground" />
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Padi · 2.5 ha</div>
                  <div className="text-sm font-semibold">Total ~16 ton</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Features() {
  const containerRef = useRef<HTMLElement>(null);
  const headingRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);
  const iconRefs = useRef<(HTMLDivElement | null)[]>([]);

  const items = [
    {
      icon: Brain,
      title: "Prediksi Yield ML",
      desc: "Random Forest memprediksi ton/ha dengan confidence interval.",
    },
    {
      icon: Sparkles,
      title: "Saran Bisnis GenAI",
      desc: "Ollama LLM mengubah angka jadi saran tindakan praktis.",
    },
    {
      icon: CloudSun,
      title: "Data Otomatis",
      desc: "Open-Meteo, SoilGrids, dan BPS dipanggil otomatis.",
    },
    {
      icon: BarChart3,
      title: "Klasifikasi Status",
      desc: "Berlimpah, Normal, atau Gagal Panen — jelas dan visual.",
    },
    { icon: Leaf, title: "Mobile-First", desc: "Didesain untuk smartphone di kondisi outdoor." },
    {
      icon: MapPin,
      title: "Riwayat Prediksi",
      desc: "Simpan dan bandingkan prediksi antar musim tanam.",
    },
  ];

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.set([headingRef.current, ...cardsRef.current], { opacity: 1 });
        return;
      }

      gsap.fromTo(
        headingRef.current,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          scrollTrigger: {
            trigger: headingRef.current,
            start: "top 85%",
            once: true,
          },
        },
      );

      gsap.fromTo(
        cardsRef.current,
        { opacity: 0, y: 50, scale: 0.95 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.5,
          stagger: 0.08,
          ease: "power3.out",
          scrollTrigger: {
            trigger: containerRef.current,
            start: "top 80%",
            once: true,
          },
        },
      );
    },
    { scope: containerRef },
  );

  const onMouseEnter = (i: number) => {
    gsap.to(cardsRef.current[i], { y: -6, duration: 0.25, ease: "power2.out" });
    gsap.to(iconRefs.current[i], { scale: 1.15, rotate: 5, duration: 0.25, ease: "back.out(2)" });
  };

  const onMouseLeave = (i: number) => {
    gsap.to(cardsRef.current[i], { y: 0, duration: 0.3, ease: "power2.inOut" });
    gsap.to(iconRefs.current[i], { scale: 1, rotate: 0, duration: 0.3, ease: "power2.inOut" });
  };

  return (
    <section id="fitur" ref={containerRef} className="mx-auto max-w-7xl px-6 py-24">
      <div ref={headingRef} style={{ opacity: 0 }} className="max-w-2xl">
        <div className="text-sm font-semibold uppercase tracking-wider text-primary">Fitur</div>
        <h2 className="mt-3 text-4xl font-bold tracking-tight md:text-5xl">
          Semua yang dibutuhkan petani modern.
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Dari input sederhana sampai keputusan bisnis — sistem menangani seluruh pipeline data, ML,
          dan AI generatif.
        </p>
      </div>
      <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((f, i) => (
          <div
            key={f.title}
            ref={(el) => {
              cardsRef.current[i] = el;
            }}
            style={{ opacity: 0 }}
            onMouseEnter={() => onMouseEnter(i)}
            onMouseLeave={() => onMouseLeave(i)}
            className="group rounded-3xl border border-border/60 bg-card p-6 transition-all hover:shadow-[var(--shadow-soft)]"
          >
            <div
              ref={(el) => {
                iconRefs.current[i] = el;
              }}
              className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground"
            >
              <f.icon className="h-6 w-6" />
            </div>
            <h3 className="mt-5 text-lg font-semibold">{f.title}</h3>
            <p className="mt-2 text-sm text-muted-foreground">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function HowItWorks() {
  const containerRef = useRef<HTMLElement>(null);
  const headingRef = useRef<HTMLDivElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  const steps = [
    {
      n: "01",
      title: "Isi Data Lahan",
      desc: "Lokasi, jenis tanaman, luas, tanggal tanam — hanya 4 field.",
    },
    {
      n: "02",
      title: "Sistem Tarik Data",
      desc: "Open-Meteo, SoilGrids, BPS dipanggil otomatis di belakang layar.",
    },
    {
      n: "03",
      title: "ML & GenAI Bekerja",
      desc: "Random Forest memprediksi yield, LLM menyusun saran praktis.",
    },
    {
      n: "04",
      title: "Lihat Hasil",
      desc: "Estimasi, status lahan, dan saran bisnis dalam satu tampilan.",
    },
  ];

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.set([headingRef.current, gridRef.current?.children], { opacity: 1 });
        return;
      }

      gsap.fromTo(
        headingRef.current,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.7,
          scrollTrigger: {
            trigger: headingRef.current,
            start: "top 85%",
            once: true,
          },
        },
      );

      if (gridRef.current) {
        gsap.fromTo(
          gridRef.current.children,
          { opacity: 0, x: -30 },
          {
            opacity: 1,
            x: 0,
            duration: 0.5,
            stagger: 0.12,
            ease: "power3.out",
            scrollTrigger: {
              trigger: gridRef.current,
              start: "top 80%",
              once: true,
            },
          },
        );
      }
    },
    { scope: containerRef },
  );

  return (
    <section
      id="cara-kerja"
      ref={containerRef}
      className="border-y border-border/50 bg-[image:var(--gradient-soft)]"
    >
      <div className="mx-auto max-w-7xl px-6 py-24">
        <div ref={headingRef} style={{ opacity: 0 }} className="max-w-2xl">
          <div className="text-sm font-semibold uppercase tracking-wider text-primary">
            Cara Kerja
          </div>
          <h2 className="mt-3 text-4xl font-bold tracking-tight md:text-5xl">
            Empat langkah, hitungan detik.
          </h2>
        </div>
        <div ref={gridRef} className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((s) => (
            <div
              key={s.n}
              style={{ opacity: 0 }}
              className="rounded-3xl border border-border/60 bg-card p-6"
            >
              <div className="text-sm font-bold text-primary">{s.n}</div>
              <h3 className="mt-3 text-lg font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Stats() {
  const containerRef = useRef<HTMLElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const statRefs = useRef<(HTMLDivElement | null)[]>([]);

  const stats = [
    { v: "< 5s", l: "Waktu prediksi end-to-end" },
    { v: "85%", l: "Target akurasi model ML" },
    { v: "3", l: "Sumber data publik terintegrasi" },
    { v: "100%", l: "Bahasa Indonesia" },
  ];

  const formatStatValue = (current: number, original: string) => {
    if (original === "< 5s") return "< " + current + "s";
    if (original === "85%") return current + "%";
    if (original === "100%") return current + "%";
    if (original === "3") return String(current);
    return String(current);
  };

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.set(wrapperRef.current, { opacity: 1 });
        return;
      }

      gsap.fromTo(
        wrapperRef.current,
        { opacity: 0, y: 60 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: wrapperRef.current,
            start: "top 85%",
            once: true,
          },
        },
      );

      stats.forEach((stat, i) => {
        const targetNumber = parseInt(stat.v.replace(/[^0-9]/g, ""));
        const obj = { val: 0 };
        const element = statRefs.current[i];

        if (element) {
          gsap.to(obj, {
            val: targetNumber,
            duration: 1.8,
            ease: "power2.out",
            delay: i * 0.15,
            scrollTrigger: {
              trigger: element,
              start: "top 80%",
              once: true,
              toggleActions: "play none none none",
            },
            onUpdate: () => {
              element.textContent = formatStatValue(Math.round(obj.val), stat.v);
            },
          });
        }
      });
    },
    { scope: containerRef },
  );

  return (
    <section id="statistik" ref={containerRef} className="mx-auto max-w-7xl px-6 py-24">
      <div
        ref={wrapperRef}
        style={{ opacity: 0 }}
        className="grid gap-8 rounded-3xl border border-border/60 bg-card p-10 md:grid-cols-4"
      >
        {stats.map((s, i) => (
          <div key={s.l}>
            <div
              ref={(el) => {
                statRefs.current[i] = el;
              }}
              className="text-5xl font-extrabold tracking-tight bg-gradient-to-br from-primary to-primary-glow bg-clip-text text-transparent"
            >
              0
            </div>
            <div className="mt-2 text-sm text-muted-foreground">{s.l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function CTA() {
  const containerRef = useRef<HTMLElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.set([cardRef.current, contentRef.current], { opacity: 1 });
        return;
      }

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top 85%",
          once: true,
        },
      });

      tl.fromTo(
        cardRef.current,
        { opacity: 0, y: 60, scale: 0.97 },
        { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: "power3.out" },
      ).fromTo(
        contentRef.current?.children || [],
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, stagger: 0.1, ease: "power2.out" },
        "-=0.4",
      );
    },
    { scope: containerRef },
  );

  return (
    <section ref={containerRef} className="mx-auto max-w-7xl px-6 pb-24">
      <div
        ref={cardRef}
        style={{ opacity: 0 }}
        className="relative overflow-hidden rounded-3xl bg-[image:var(--gradient-hero)] p-12 text-primary-foreground shadow-[var(--shadow-elegant)] md:p-16"
      >
        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-24 -left-10 h-64 w-64 rounded-full bg-white/10 blur-3xl" />
        <div ref={contentRef} className="relative max-w-2xl">
          <h2 style={{ opacity: 0 }} className="text-4xl font-bold tracking-tight md:text-5xl">
            Siap memprediksi panen Anda?
          </h2>
          <p style={{ opacity: 0 }} className="mt-4 text-lg text-primary-foreground/80">
            Buat prediksi pertama Anda dalam 30 detik. Gratis, tanpa instalasi.
          </p>
          <div style={{ opacity: 0 }} className="mt-8">
            <Button
              asChild
              size="lg"
              className="rounded-full bg-background text-foreground hover:bg-background/90"
            >
              <Link to="/login">
                Masuk ke Dashboard <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-border/50">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 py-8 md:flex-row">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[image:var(--gradient-hero)]">
            <Sprout className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="text-sm font-semibold">Agri Trend DSS</span>
        </div>
        <p className="text-xs text-muted-foreground">© 2026 Capstone Project · PJK-GM023</p>
      </div>
    </footer>
  );
}
