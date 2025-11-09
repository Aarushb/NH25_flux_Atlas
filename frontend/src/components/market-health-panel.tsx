import { useEffect, useState, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";

function easeOutCubic(t: number) {
  return 1 - Math.pow(1 - t, 3);
}

function ParallaxWrapper({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const rafRef = useRef<number | null>(null);
  const [style, setStyle] = useState<Record<string, string>>({ transform: "none" });

  useEffect(() => {
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, []);

  const onMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width - 0.5; // -0.5 .. 0.5
    const py = (e.clientY - rect.top) / rect.height - 0.5;
    const tx = px * 10; // translateX px
    const ty = py * 8; // translateY px
    const rx = -py * 4; // rotateX deg
    const ry = px * 6; // rotateY deg

    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      setStyle({
        transform: `perspective(900px) translate3d(${tx}px, ${ty}px, 0) rotateX(${rx}deg) rotateY(${ry}deg)`,
      });
    });
  };

  const onLeave = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    setStyle({ transform: "perspective(900px) translate3d(0,0,0) rotateX(0deg) rotateY(0deg)" });
  };

  return (
    <div ref={ref} onMouseMove={onMove} onMouseLeave={onLeave} style={style} className="parallax-inner">
      {children}
    </div>
  );
}

function CountUp({ to, duration = 1800, start = true, startDelay = 0 }: { to: number; duration?: number; start?: boolean; startDelay?: number }) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!start) return;
  let raf = 0;
    let cancelled = false;
    const run = () => {
      const t0 = performance.now();
      const step = (now: number) => {
        if (cancelled) return;
        const raw = Math.min(1, (now - t0) / duration);
        const t = easeOutCubic(raw);
        setValue(Math.floor(to * t));
        if (raw < 1) raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    };

    let timer: number | undefined;
    if (startDelay > 0) timer = window.setTimeout(run, startDelay);
    else run();

    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      if (timer) clearTimeout(timer);
    };
  }, [to, duration, start, startDelay]);

  return <div className="text-3xl font-bold">{value}</div>;
}

function Sparkline({ data = [4, 8, 6, 10, 12, 9], start = true, startDelay = 0 }: { data?: number[]; start?: boolean; startDelay?: number }) {
  const w = 140;
  const h = 40;
  const max = Math.max(...data);
  const points = data.map((d, i) => `${(i / (data.length - 1)) * w},${h - (d / max) * h}`);
  const d = `M ${points.map((p) => p.replace(",", " ")).join(" L ")}`;
  const pathRef = useRef<SVGPathElement | null>(null);

  useEffect(() => {
    const path = pathRef.current;
    if (!path) return;
    if (!start) return;
    let raf = 0;
    let cancelled = false;
    const run = () => {
      const len = path.getTotalLength();
      path.style.strokeDasharray = String(len);
      path.style.strokeDashoffset = String(len);
  const duration = 1400;
      const t0 = performance.now();
      const step = (now: number) => {
        if (cancelled) return;
        const raw = Math.min(1, (now - t0) / duration);
        const t = easeOutCubic(raw);
        path.style.strokeDashoffset = String(Math.floor(len * (1 - t)));
        if (raw < 1) raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    };
    let timer: number | undefined;
    if (startDelay > 0) timer = window.setTimeout(run, startDelay);
    else run();
    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      if (timer) clearTimeout(timer);
    };
  }, [d, start, startDelay]);

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} fill="none" aria-hidden>
      <path ref={pathRef} d={d} fill="none" stroke="#00ff7f" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function CircularProgress({ percent = 65, start = true, startDelay = 0 }: { percent?: number; start?: boolean; startDelay?: number }) {
  const size = 80;
  const stroke = 8;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const [offset, setOffset] = useState(circumference);
  const targetOffset = circumference - (percent / 100) * circumference;
  useEffect(() => {
    if (!start) return;
    let raf = 0;
    let cancelled = false;
    const run = () => {
  const duration = 1600;
      const t0 = performance.now();
      const startOffset = circumference;
      const step = (now: number) => {
        if (cancelled) return;
        const raw = Math.min(1, (now - t0) / duration);
        const t = easeOutCubic(raw);
        const cur = startOffset + (targetOffset - startOffset) * t;
        setOffset(cur);
        if (raw < 1) raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    };
    let timer: number | undefined;
    if (startDelay > 0) timer = window.setTimeout(run, startDelay);
    else run();
    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      if (timer) clearTimeout(timer);
    };
  }, [circumference, targetOffset, start, startDelay]);

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
      <defs>
        <linearGradient id="g1" x1="0" x2="1">
          <stop offset="0%" stopColor="#00ff7f" />
          <stop offset="100%" stopColor="#008080" />
        </linearGradient>
      </defs>
      <circle cx={size / 2} cy={size / 2} r={radius} stroke="rgba(255,255,255,0.06)" strokeWidth={stroke} fill="none" />
      <circle cx={size / 2} cy={size / 2} r={radius} stroke="url(#g1)" strokeWidth={stroke} fill="none" strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" transform={`rotate(-90 ${size / 2} ${size / 2})`} />
      <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" fill="var(--foreground)" fontSize="12" fontWeight="700">{`${percent}%`}</text>
    </svg>
  );
}

function SpiderChart({ values = [0.6, 0.7, 0.5, 0.8, 0.65], start = true, startDelay = 0 }: { values?: number[]; start?: boolean; startDelay?: number }) {
  const size = 140;
  const cx = size / 2;
  const cy = size / 2;
  const r = 52;
  const [scale, setScale] = useState(0);

  useEffect(() => {
    if (!start) return;
    let raf = 0;
    let cancelled = false;
    const run = () => {
  const duration = 1400;
      const t0 = performance.now();
      const step = (now: number) => {
        if (cancelled) return;
        const raw = Math.min(1, (now - t0) / duration);
        const t = easeOutCubic(raw);
        setScale(t);
        if (raw < 1) raf = requestAnimationFrame(step);
      };
      raf = requestAnimationFrame(step);
    };
    let timer: number | undefined;
    if (startDelay > 0) timer = window.setTimeout(run, startDelay);
    else run();
    return () => {
      cancelled = true;
      cancelAnimationFrame(raf);
      if (timer) clearTimeout(timer);
    };
  }, [start, startDelay]);

  const points = values.map((v, i) => {
    const angle = (Math.PI * 2 * i) / values.length - Math.PI / 2;
    const x = cx + Math.cos(angle) * r * v * scale;
    const y = cy + Math.sin(angle) * r * v * scale;
    return `${x},${y}`;
  });
  const ideal = values.map((_, i) => {
    const angle = (Math.PI * 2 * i) / values.length - Math.PI / 2;
    const x = cx + Math.cos(angle) * r * 0.95 * scale;
    const y = cy + Math.sin(angle) * r * 0.95 * scale;
    return `${x},${y}`;
  });
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-hidden>
      <polygon points={ideal.join(" ")} fill="none" stroke="#d2691e33" strokeWidth={1.5} />
      <polygon points={points.join(" ")} fill="#d2691e66" stroke="#d2691e" strokeWidth={1.5} />
    </svg>
  );
}

export default function MarketHealthPanel() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const onGone = () => setReady(true);
    // If landing hero is not present, start immediately
    const landing = document.querySelector('.landing-hero');
    if (!landing) {
      setReady(true);
      return;
    }
    window.addEventListener('landing:gone', onGone);
    return () => window.removeEventListener('landing:gone', onGone);
  }, []);

  return (
    <div className="market-health grid grid-cols-1 sm:grid-cols-3 gap-4 items-stretch">
      <Card data-parallax="true">
        <ParallaxWrapper>
          <CardContent className="flex flex-col gap-2 items-start">
          <div className="text-sm text-muted-foreground">Projected Global Welfare Score</div>
          <div className="flex items-center gap-4 w-full justify-between">
              <div className="flex flex-col">
              <CountUp to={87} start={ready} startDelay={350} />
              <div className="text-xs text-muted-foreground">Economic Value Creation</div>
            </div>
            <div className="ml-auto">
              <Sparkline start={ready} startDelay={700} />
            </div>
          </div>
          </CardContent>
        </ParallaxWrapper>
      </Card>

      <Card data-parallax="true">
        <ParallaxWrapper>
          <CardContent className="flex flex-col items-center justify-center gap-2">
          <div className="text-sm text-muted-foreground">Carbon Reduction</div>
          <CircularProgress percent={65} start={ready} startDelay={1100} />
          <div className="text-xs text-muted-foreground">65% Reduction</div>
          </CardContent>
        </ParallaxWrapper>
      </Card>

      <Card data-parallax="true">
        <ParallaxWrapper>
          <CardContent className="flex flex-col items-center gap-2">
          <div className="text-sm text-muted-foreground">Fairness Index</div>
          <SpiderChart start={ready} startDelay={1500} />
          <div className="text-xs text-muted-foreground">Current vs Ideal</div>
          </CardContent>
        </ParallaxWrapper>
      </Card>
    </div>
  );
}
