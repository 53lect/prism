const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface PairSummary {
  symbol: string;
  last_signal: "LONG" | "SHORT" | "NEUTRAL" | null;
  last_confidence: number | null;
  last_price: number | null;
  last_analyzed_at: string | null;
  valid: boolean | null;
}

export interface SignalRecord {
  id: number;
  symbol: string;
  analyzed_at: string;
  signal: "LONG" | "SHORT" | "NEUTRAL";
  confidence: number;
  price: number;
  rsi_14: number;
  expected_value: number;
  risk_score: number;
  stop_loss_pct: number;
  take_profit_pct: number;
  reasoning: string;
  valid: boolean;
}

export interface AnalysisResult {
  symbol: string;
  market: Record<string, number | string>;
  sentiment: Record<string, number | string>;
  news: Record<string, number | string | string[]>;
  macro: Record<string, number | string>;
  risk: Record<string, number | boolean>;
  synthesis: {
    signal: "LONG" | "SHORT" | "NEUTRAL";
    confidence: number;
    stop_loss_pct: number;
    take_profit_pct: number;
    reasoning: string;
    key_risk: string;
    from_cache: boolean;
  };
}

export async function fetchPairs(): Promise<PairSummary[]> {
  const res = await fetch(`${BASE}/pairs/`, { cache: "no-store" });
  return res.json();
}

export async function fetchHistory(pair?: string, limit = 50): Promise<SignalRecord[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (pair) params.set("pair", pair);
  const res = await fetch(`${BASE}/signals/history?${params}`, { cache: "no-store" });
  return res.json();
}

export async function analyzePair(pair: string): Promise<AnalysisResult> {
  const res = await fetch(`${BASE}/analyze/${pair}`, { method: "POST" });
  return res.json();
}
