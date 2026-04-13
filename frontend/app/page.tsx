import { fetchPairs, fetchKlines } from "@/lib/api";
import PairCard from "@/components/PairCard";
import LiveUpdater from "@/components/LiveUpdater";

export default async function Dashboard() {
  const pairs = await fetchPairs();

  // Fetch sparkline data (24 velas de 1h) para todas las cards en paralelo
  const klinesPerPair = await Promise.all(
    pairs.map((p) =>
      fetchKlines(p.symbol, "1h", 24).catch(() => [])
    )
  );

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-4 sm:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Prism</h1>
            <p className="text-zinc-400 text-sm mt-1">Análisis crypto — Binance Perpetual Futures</p>
          </div>
          <LiveUpdater />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {pairs.map((pair, i) => (
            <PairCard
              key={pair.symbol}
              pair={pair}
              closes={klinesPerPair[i].map((k) => k.close)}
            />
          ))}
        </div>
      </div>
    </main>
  );
}
