import { analyzePair } from "@/lib/api";
import Link from "next/link";
import Chart from "@/components/Chart";

export default async function PairDetail({ params }: { params: Promise<{ symbol: string }> }) {
  const { symbol } = await params;
  const data = await analyzePair(symbol);
  const { market: m, sentiment: s, news: n, macro: mac, risk: r, synthesis: syn } = data;

  const signalColor =
    syn.signal === "LONG"  ? "text-emerald-400" :
    syn.signal === "SHORT" ? "text-red-400" :
    "text-zinc-400";

  const ts = syn.trade_suggestion;

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-4 sm:p-8">
      <div className="max-w-3xl mx-auto space-y-4">
        <Link href="/" className="text-zinc-500 hover:text-zinc-300 text-sm inline-block">← Dashboard</Link>

        {/* Header */}
        <div className="flex flex-wrap items-center gap-3">
          <h1 className="text-3xl font-bold font-mono">{symbol}</h1>
          <span className={`text-2xl font-bold ${signalColor}`}>{syn.signal}</span>
          <span className="text-zinc-400">{syn.confidence}% confianza</span>
          {syn.from_cache && <span className="text-xs bg-zinc-800 px-2 py-1 rounded text-zinc-500">CACHE</span>}
        </div>

        {/* Chart con selector de temporalidad */}
        <Chart symbol={symbol} />

        {/* Síntesis */}
        <Section title="Síntesis">
          <p className="text-zinc-300 leading-relaxed">{syn.reasoning}</p>
          <p className="text-red-400/80 text-sm mt-2">Riesgo: {syn.key_risk}</p>
          <div className="grid grid-cols-2 gap-3 mt-3">
            <Stat label="Stop-loss" value={`-${syn.stop_loss_pct?.toFixed(3)}%`} />
            <Stat label="Take-profit" value={`+${syn.take_profit_pct?.toFixed(3)}%`} />
          </div>
        </Section>

        {/* Trade sugerido */}
        {ts && (
          <Section title="Trade sugerido">
            <div className="flex items-center gap-3 mb-3">
              <span className={`font-bold text-lg ${ts.direction === "LONG" ? "text-emerald-400" : ts.direction === "SHORT" ? "text-red-400" : "text-zinc-400"}`}>
                {ts.direction}
              </span>
              <span className={`text-xs px-2 py-1 rounded font-semibold ${ts.advisable ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"}`}>
                {ts.advisable ? "Aconsejable" : "No aconsejable"}
              </span>
            </div>
            <p className="text-zinc-300 text-sm">{ts.entry_note}</p>
            <p className="text-zinc-500 text-sm mt-1">{ts.reason}</p>
          </Section>
        )}

        {/* Risk */}
        <Section title="Layer 5 — Riesgo">
          <div className="grid grid-cols-2 gap-2">
            <Stat label="Position size" value={`${r.position_size_pct}%`} />
            <Stat label="Break-even" value={`${Number(r.fee_breakeven_pct).toFixed(3)}%`} />
            <Stat label="EV" value={`${Number(r.expected_value).toFixed(4)}%`} />
            <Stat label="VaR 95%" value={`${Number(r.var_95_pct).toFixed(3)}%`} />
            <Stat label="Risk score" value={`${r.risk_score}/100`} />
            <Stat label="Válida" value={r.valid ? "SI" : "NO"} />
          </div>
        </Section>

        {/* Market data */}
        <Section title="Layer 1 — Market Data">
          <div className="grid grid-cols-2 gap-2">
            <Stat label="Precio" value={`$${Number(m.price).toLocaleString()}`} />
            <Stat label="Cambio 24h" value={`${Number(m.change_24h).toFixed(2)}%`} />
            <Stat label="RSI-14" value={String(m.rsi_14)} />
            <Stat label="Volatilidad" value={`${Number(m.volatility).toFixed(3)}%`} />
            <Stat label="Funding rate" value={`${Number(m.funding_rate).toFixed(4)}%`} />
            <Stat label="Liquidez" value={`${m.liquidity_score}/100`} />
          </div>
        </Section>

        {/* Sentimiento + Macro en grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Section title="Layer 2 — Sentimiento">
            <Stat label="Fear & Greed" value={`${s.fear_greed_index} (${s.fear_greed_label})`} />
            <div className="mt-1">
              <Stat label="Score" value={String(s.sentiment_score)} />
            </div>
          </Section>

          <Section title="Layer 4 — Macro">
            <Stat label="BTC Dominance" value={`${Number(mac.btc_dominance).toFixed(1)}%`} />
            <div className="mt-1">
              <Stat label="Mercado 24h" value={`${Number(mac.market_cap_change_24h).toFixed(2)}%`} />
            </div>
            <div className="mt-1">
              <Stat label="Tendencia" value={String(mac.market_trend)} />
            </div>
          </Section>
        </div>

        {/* Noticias */}
        <Section title="Layer 3 — Noticias">
          <div className="grid grid-cols-2 gap-2 mb-3">
            <Stat label="Encontradas" value={String(n.news_count)} />
            <Stat label="Score" value={String(n.sentiment_score)} />
          </div>
          {Array.isArray(n.headlines) && n.headlines.length > 0 && (
            <ul className="space-y-1">
              {(n.headlines as string[]).map((h, i) => (
                <li key={i} className="text-zinc-400 text-sm">· {h}</li>
              ))}
            </ul>
          )}
        </Section>
      </div>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-widest mb-3">{title}</h2>
      {children}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-zinc-500">{label}</span>
      <span className="font-mono">{value}</span>
    </div>
  );
}
