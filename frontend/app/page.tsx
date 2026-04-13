import { fetchPairs } from "@/lib/api";
import PairCard from "@/components/PairCard";
import LiveUpdater from "@/components/LiveUpdater";

export default async function Dashboard() {
  const pairs = await fetchPairs();

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Prism</h1>
            <p className="text-zinc-400 text-sm mt-1">Análisis crypto — Binance Perpetual Futures</p>
          </div>
          <LiveUpdater />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {pairs.map((pair) => (
            <PairCard key={pair.symbol} pair={pair} />
          ))}
        </div>
      </div>
    </main>
  );
}
