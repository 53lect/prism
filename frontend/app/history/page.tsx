import { fetchHistory } from "@/lib/api";
import Link from "next/link";

export default async function History({ searchParams }: { searchParams: Promise<{ pair?: string }> }) {
  const { pair } = await searchParams;
  const records = await fetchHistory(pair, 100);

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-5xl mx-auto">
        <Link href="/" className="text-zinc-500 hover:text-zinc-300 text-sm mb-6 inline-block">← Dashboard</Link>
        <h1 className="text-2xl font-bold mb-6">Historial de señales</h1>

        {records.length === 0 ? (
          <p className="text-zinc-500">Sin señales registradas todavía.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-zinc-500 text-xs uppercase tracking-wider border-b border-zinc-800">
                  <th className="text-left py-2 pr-4">Par</th>
                  <th className="text-left py-2 pr-4">Señal</th>
                  <th className="text-right py-2 pr-4">Conf.</th>
                  <th className="text-right py-2 pr-4">Precio</th>
                  <th className="text-right py-2 pr-4">EV</th>
                  <th className="text-right py-2 pr-4">RSI</th>
                  <th className="text-left py-2">Fecha</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => {
                  const signalColor =
                    r.signal === "LONG" ? "text-emerald-400" :
                    r.signal === "SHORT" ? "text-red-400" :
                    "text-zinc-400";
                  return (
                    <tr key={r.id} className="border-b border-zinc-800/50 hover:bg-zinc-900/50">
                      <td className="py-2 pr-4 font-mono font-semibold">{r.symbol}</td>
                      <td className={`py-2 pr-4 font-bold ${signalColor}`}>{r.signal}</td>
                      <td className="py-2 pr-4 text-right font-mono">{r.confidence}%</td>
                      <td className="py-2 pr-4 text-right font-mono">${r.price.toFixed(4)}</td>
                      <td className="py-2 pr-4 text-right font-mono">{r.expected_value.toFixed(4)}%</td>
                      <td className="py-2 pr-4 text-right font-mono">{r.rsi_14?.toFixed(1)}</td>
                      <td className="py-2 text-zinc-400 text-xs">{new Date(r.analyzed_at).toLocaleString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
