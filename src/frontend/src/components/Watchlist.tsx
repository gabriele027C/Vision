import { useState } from "react";
import type { AppState, WatchRow } from "../types";
import WatchTable from "./WatchTable";

export default function Watchlist({
  state,
  onPlan,
}: {
  state: AppState | null;
  onPlan: (row: WatchRow) => void;
}) {
  const [market, setMarket] = useState<"crypto" | "stocks">("crypto");
  const rows = state?.watchlist[market] ?? [];

  return (
    <>
      <div className="row section">
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
        <span className="muted">
          Top {rows.length} per forza relativa con Setup A/B valido — verifica sempre il grafico su
          TradingView prima di ordinare.
        </span>
      </div>
      <div className="card">
        <WatchTable rows={rows} market={market} onPlan={onPlan} />
      </div>
    </>
  );
}
