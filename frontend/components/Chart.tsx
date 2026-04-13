"use client";

import { useEffect, useRef, useState } from "react";
import { createChart, CandlestickSeries, IChartApi } from "lightweight-charts";
import { fetchKlines, Interval, Kline } from "@/lib/api";

const INTERVALS: { label: string; value: Interval }[] = [
  { label: "15m", value: "15m" },
  { label: "1h",  value: "1h" },
  { label: "4h",  value: "4h" },
  { label: "1d",  value: "1d" },
];

export default function Chart({ symbol }: { symbol: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ReturnType<IChartApi["addSeries"]> | null>(null);
  const [interval, setInterval] = useState<Interval>("1h");
  const [loading, setLoading] = useState(true);

  // Crear chart una sola vez
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: "#18181b" },
        textColor: "#a1a1aa",
      },
      grid: {
        vertLines: { color: "#27272a" },
        horzLines: { color: "#27272a" },
      },
      timeScale: { timeVisible: true, secondsVisible: false },
      width: containerRef.current.clientWidth,
      height: 320,
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#34d399",
      downColor: "#f87171",
      borderUpColor: "#34d399",
      borderDownColor: "#f87171",
      wickUpColor: "#34d399",
      wickDownColor: "#f87171",
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const observer = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    });
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      chart.remove();
    };
  }, []);

  // Cargar datos cuando cambia el intervalo
  useEffect(() => {
    if (!seriesRef.current) return;
    setLoading(true);

    fetchKlines(symbol, interval, 150).then((klines: Kline[]) => {
      seriesRef.current!.setData(
        klines.map((k) => ({
          time: k.time as unknown as import("lightweight-charts").Time,
          open: k.open,
          high: k.high,
          low: k.low,
          close: k.close,
        }))
      );
      chartRef.current?.timeScale().fitContent();
      setLoading(false);
    });
  }, [symbol, interval]);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Gráfico</h2>
        <div className="flex gap-1">
          {INTERVALS.map((i) => (
            <button
              key={i.value}
              onClick={() => setInterval(i.value)}
              className={`px-3 py-1 text-xs rounded font-mono transition-colors ${
                interval === i.value
                  ? "bg-zinc-700 text-zinc-100"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {i.label}
            </button>
          ))}
        </div>
      </div>
      <div className="relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-900/80 rounded z-10">
            <span className="text-zinc-500 text-sm">Cargando...</span>
          </div>
        )}
        <div ref={containerRef} className="w-full" />
      </div>
    </div>
  );
}
