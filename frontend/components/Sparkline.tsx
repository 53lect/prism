"use client";

interface SparklineProps {
  closes: number[];
  positive?: boolean;
}

export default function Sparkline({ closes, positive }: SparklineProps) {
  if (closes.length < 2) return null;

  const min = Math.min(...closes);
  const max = Math.max(...closes);
  const range = max - min || 1;

  const w = 200;
  const h = 48;
  const pad = 2;

  const points = closes.map((v, i) => {
    const x = pad + (i / (closes.length - 1)) * (w - pad * 2);
    const y = h - pad - ((v - min) / range) * (h - pad * 2);
    return `${x},${y}`;
  });

  const pathD = `M ${points.join(" L ")}`;
  const first = closes[0];
  const last = closes[closes.length - 1];
  const isUp = last >= first;
  const color = isUp ? "#34d399" : "#f87171";

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-12" preserveAspectRatio="none">
      <path d={pathD} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
    </svg>
  );
}
