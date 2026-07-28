import { useState } from "react";
import type { AppState, WatchRow } from "../types";
import RegimeCard from "./RegimeCard";
import WatchTable from "./WatchTable";

export default function Watchlist({
  state,
  onPlan,
}: {
  state: AppState | null;
  onPlan: (row: WatchRow) => void;
}) {
  const [market, setMarket] = useState<"crypto" | "stocks">("crypto");
  const [tab, setTab] = useState<"long" | "bearish">("long");
  const rows = state?.watchlist[market] ?? [];
  const bearish = state?.bearish_context?.[market] ?? [];
  const regime = state?.regimes?.[market];

  return (
    <>
      <div className="row section" style={{ alignItems: "flex-start", gap: 16 }}>
        <div>
          <div className="tabs">
            <button
              className={`tab ${market === "crypto" ? "active" : ""}`}
              onClick={() => setMarket("crypto")}
            >
              Crypto
            </button>
            <button
              className={`tab ${market === "stocks" ? "active" : ""}`}
              onClick={() => setMarket("stocks")}
            >
              Azioni
            </button>
          </div>
          <div className="tabs" style={{ marginTop: 8 }}>
            <button
              className={`tab ${tab === "long" ? "active" : ""}`}
              onClick={() => setTab("long")}
            >
              Watchlist long ({rows.length})
            </button>
            <button
              className={`tab ${tab === "bearish" ? "active" : ""}`}
              onClick={() => setTab("bearish")}
            >
              Contesto ribassista ({bearish.length})
            </button>
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <RegimeCard
            title={market === "crypto" ? "Contesto regime crypto (informativo)" : "Contesto regime azioni (informativo)"}
            regime={regime}
          />
          <p className="muted" style={{ marginTop: 8 }}>
            Situazioni ordinate per forza relativa. I pattern non hanno edge statistico dimostrato —
            usa sizing e journal. Verifica sempre il grafico su TradingView.
          </p>
        </div>
      </div>

      {tab === "long" && (
        <div className="card">
          {market === "crypto" && rows.length === 0 && regime?.mode === "short" && (
            <div className="empty" style={{ textAlign: "left", padding: 16 }}>
              <strong>Regime ribassista: lato long senza contesto operativo</strong>
              <p className="muted" style={{ marginTop: 8, marginBottom: 8 }}>
                Il sistema sta funzionando, non è un errore. In regime short non
                popoliamo la watchlist long: non ci sono situazioni long operative da
                seguire ora.
              </p>
              <p style={{ marginBottom: 0 }}>
                <button type="button" className="btn small" onClick={() => setTab("bearish")}>
                  Apri tab Contesto ribassista
                </button>
                {" · "}
                <a href="#playbook-contesto-ribassista" className="ticker-link">
                  Scheda playbook contesto_ribassista
                </a>
              </p>
            </div>
          )}
          {(rows.length > 0 || !(market === "crypto" && regime?.mode === "short")) && (
            <WatchTable rows={rows} market={market} onPlan={onPlan} />
          )}
        </div>
      )}

      {tab === "bearish" && (
        <div className="card">
          <h3>Contesto ribassista (solo informativo)</h3>
          <p className="muted">
            Nessun livello operativo né alert. Situazioni sotto EMA50 rilevate dal motore —
            non sono raccomandazioni short.
          </p>
          {bearish.length === 0 && <div className="empty">Nessun contesto ribassista al momento.</div>}
          {bearish.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Setup</th>
                  <th>RS</th>
                  <th>RVOL</th>
                  <th>Prezzo</th>
                  <th>Nota</th>
                </tr>
              </thead>
              <tbody>
                {bearish.map((r) => (
                  <tr key={r.symbol}>
                    <td>{r.symbol}</td>
                    <td>{r.setup}</td>
                    <td className="mono">{(r.rs_score * 100).toFixed(0)}%</td>
                    <td className="mono">{r.rvol.toFixed(2)}</td>
                    <td className="mono">{r.last_price}</td>
                    <td className="muted">{r.note}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  );
}
