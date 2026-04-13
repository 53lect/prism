"use client";

import Link from "next/link";
import { PairSummary } from "@/lib/api";

const SIGNAL_STYLES = {
  LONG: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  SHORT: "bg-red-500/20 text-red-400 border-red-500/30",
  NEUTRAL: "bg-zinc-700/40 text-zinc-400 border-zinc-600/30",
};

export default function PairCard({ pair }: { pair: PairSummary }) {
  const signal = pair.last_signal ?? "NEUTRAL";
  const style = SIGNAL_STYLES[signal];

  return (
    <Link href={`/pair/${pair.symbol}`}>
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 hover:border-zinc-600 transition-colors cursor-pointer">
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono font-semibold text-lg">{pair.symbol.replace("USDT", "")}<span className="text-zinc-500 text-sm font-normal">/USDT</span></span>
          <span className={`text-xs font-bold px-2 py-1 rounded border ${style}`}>{signal}</span>
        </div>

        <div className="space-y-1 text-sm">
          {pair.last_price != null && (
            <div className="flex justify-between">
              <span className="text-zinc-500">Precio</span>
              <span className="font-mono">${pair.last_price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 4 })}</span>
            </div>
          )}
          {pair.last_confidence != null && (
            <div className="flex justify-between">
              <span className="text-zinc-500">Confianza</span>
              <span className="font-mono">{pair.last_confidence}%</span>
            </div>
          )}
          {pair.last_analyzed_at && (
            <div className="flex justify-between">
              <span className="text-zinc-500">Último análisis</span>
              <span className="text-zinc-400 text-xs">{new Date(pair.last_analyzed_at).toLocaleTimeString()}</span>
            </div>
          )}
          {pair.last_price == null && (
            <p className="text-zinc-600 text-xs text-center pt-2">Sin datos — ejecutar análisis</p>
          )}
        </div>
      </div>
    </Link>
  );
}
