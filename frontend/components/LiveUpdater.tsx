"use client";

import { useEffect, useState } from "react";

interface LiveUpdate {
  symbol: string;
  signal: string;
  confidence: number;
  price: number;
  from_cache: boolean;
}

export default function LiveUpdater() {
  const [status, setStatus] = useState<"connecting" | "live" | "disconnected">("connecting");
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  useEffect(() => {
    const wsUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000")
      .replace("http://", "ws://")
      .replace("https://", "wss://");

    let ws: WebSocket;

    function connect() {
      ws = new WebSocket(`${wsUrl}/ws/live`);

      ws.onopen = () => setStatus("live");

      ws.onmessage = (event) => {
        const updates: LiveUpdate[] = JSON.parse(event.data);
        setLastUpdate(new Date().toLocaleTimeString());
        // Recargar la página para reflejar los nuevos datos del servidor
        if (updates.some((u) => !u.from_cache)) {
          window.location.reload();
        }
      };

      ws.onclose = () => {
        setStatus("disconnected");
        setTimeout(connect, 5000); // reconectar en 5s
      };
    }

    connect();
    return () => ws?.close();
  }, []);

  const dot =
    status === "live" ? "bg-emerald-500 animate-pulse" :
    status === "connecting" ? "bg-yellow-500 animate-pulse" :
    "bg-red-500";

  return (
    <div className="flex items-center gap-2 text-xs text-zinc-500">
      <span className={`w-2 h-2 rounded-full ${dot}`} />
      {status === "live" ? `Live${lastUpdate ? ` · ${lastUpdate}` : ""}` :
       status === "connecting" ? "Conectando..." : "Desconectado"}
    </div>
  );
}
