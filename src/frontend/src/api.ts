import type { AppState, AssetDiagnostics, DiagnosticsResponse, Metrics, Settings, Sizing, Trade } from "./types";

async function http<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    const body = await resp.json().catch(() => null);
    throw new Error(body?.detail ?? `Errore ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  state: () => http<AppState>("/api/state"),
  scan: () => http<{ started: boolean }>("/api/scan", { method: "POST" }),
  readAlerts: () => http("/api/alerts/read", { method: "POST" }),
  sizing: (entry: number, stop: number, half_size: boolean) =>
    http<Sizing>("/api/sizing", {
      method: "POST",
      body: JSON.stringify({ entry, stop, half_size }),
    }),
  trades: () => http<Trade[]>("/api/trades"),
  createTrade: (t: Partial<Trade>) =>
    http<Trade>("/api/trades", { method: "POST", body: JSON.stringify(t) }),
  closeTrade: (id: number, exit_price: number, mistake: boolean, notes: string) =>
    http<Trade>(`/api/trades/${id}/close`, {
      method: "PUT",
      body: JSON.stringify({ exit_price, mistake, notes }),
    }),
  deleteTrade: (id: number) => http(`/api/trades/${id}`, { method: "DELETE" }),
  metrics: () => http<Metrics>("/api/metrics"),
  settings: () => http<Settings>("/api/settings"),
  saveSettings: (s: Partial<Settings>) =>
    http<Settings>("/api/settings", { method: "PUT", body: JSON.stringify(s) }),
  testTelegram: () => http("/api/settings/telegram/test", { method: "POST" }),
  diagnostics: (market: "crypto" | "stocks", symbols?: string) =>
    http<DiagnosticsResponse>(
      `/api/diagnostics/${market}${symbols ? `?symbols=${encodeURIComponent(symbols)}` : ""}`
    ),
  diagnosticSymbol: (market: "crypto" | "stocks", symbol: string) =>
    http<AssetDiagnostics>(`/api/diagnostics/${market}/${encodeURIComponent(symbol)}`),
};
