import { useRef } from "react";
import { Sprout } from "lucide-react";
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";

interface SplashScreenProps {
  onComplete: () => void;
}

export const SplashScreen = ({ onComplete }: SplashScreenProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const iconRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLHeadingElement>(null);
  const barRef = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        onComplete();
        return;
      }

      const tl = gsap.timeline({
        onComplete: () => {
          onComplete();
        },
      });

      // t=0.0: ikon dan teks fade in dari bawah
      tl.fromTo(
        [iconRef.current, textRef.current],
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6, ease: "power3.out", stagger: 0.1 },
        0,
      );

      // t=0.4: loading bar fill animasi dari width 0% ke 100%
      tl.fromTo(
        barRef.current,
        { width: "0%" },
        { width: "100%", duration: 1.4, ease: "power2.inOut" },
        0.4,
      );

      // t=1.6: seluruh overlay fade out
      tl.to(containerRef.current, { opacity: 0, duration: 0.5, ease: "power2.in" }, 1.6);
    },
    { scope: containerRef },
  );

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#2D6A4F] text-white"
    >
      <div className="flex flex-col items-center gap-4">
        <div ref={iconRef} style={{ opacity: 0 }}>
          <Sprout size={48} />
        </div>
        <h1 ref={textRef} style={{ opacity: 0 }} className="text-2xl font-bold">
          Agri Trend DSS
        </h1>
        <div className="relative mt-4 h-[3px] w-48 overflow-hidden rounded-full bg-white/40">
          <div ref={barRef} className="absolute inset-y-0 left-0 bg-white" style={{ width: 0 }} />
        </div>
      </div>
    </div>
  );
};
