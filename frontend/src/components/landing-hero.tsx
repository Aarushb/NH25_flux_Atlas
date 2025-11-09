import { useEffect, useState } from "react";

function formatNumber(n: number) {
  return n.toLocaleString();
}

function formatMoney(n: number) {
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

export default function LandingHero() {
  const [visible, setVisible] = useState(true);
  const [finished, setFinished] = useState(false);
  const [carbon, setCarbon] = useState(0);
  const [countries, setCountries] = useState(0);
  const [value, setValue] = useState(0);

  useEffect(() => {
    let raf = 0;
    const animate = (from: number, to: number, duration: number, cb: (v: number) => void, onDone?: () => void) => {
      const start = performance.now();
      const step = (now: number) => {
        const t = Math.min(1, (now - start) / duration);
        const v = Math.floor(from + (to - from) * t);
        cb(v);
        if (t < 1) raf = requestAnimationFrame(step);
        else onDone?.();
      };
      raf = requestAnimationFrame(step);
    };

    animate(0, 1250000, 1400, setCarbon, () => {
      animate(0, 47, 900, setCountries, () => {
        animate(0, 2800000000, 1600, setValue, () => setFinished(true));
      });
    });

    return () => cancelAnimationFrame(raf);
  }, []);

  const onArrowClick = () => {
    const target = document.getElementById("main-content");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
      setTimeout(() => setVisible(false), 700);
    } else {
      setVisible(false);
    }
  };

  useEffect(() => {
    if (!visible) {
      window.dispatchEvent(new CustomEvent('landing:gone'));
    }
  }, [visible]);

  if (!visible) return null;

  return (
    <div className="landing-hero" role="region" aria-label="Landing Hero">
      <div className="landing-inner">
        <h2 className="landing-title">Building an Efficient Global Resource Market</h2>
        <div className="landing-stats">
          <div className="stat">
            <div className="stat-label">Estimated Carbon Reduced</div>
            <div className="stat-value">{formatNumber(carbon)} <span className="stat-suffix">tons</span></div>
          </div>
          <div className="stat">
            <div className="stat-label">Projected Countries Trading</div>
            <div className="stat-value">{formatNumber(countries)}</div>
          </div>
          <div className="stat">
            <div className="stat-label">Projected Economic Value Created</div>
            <div className="stat-value">{formatMoney(value)}</div>
          </div>
        </div>

        {finished && (
          <button className="landing-start-btn" aria-label="Start the fair trade" onClick={onArrowClick}>
            Start the fair trade
          </button>
        )}
      </div>
    </div>
  );
}
