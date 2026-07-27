import { api } from "../api";
import type { AppState, WatchRow } from "../types";
import RegimeCard from "./RegimeCard";
import WatchTable from "./WatchTable";

export default function Dashboard({
  state,
  onRefresh,
  onPlan,
}: {
  state: AppState | null;
  onRefresh: () => void;
  onPlan: (row: WatchRow) => void;
}) {
  const startScan = async () => {
    await api.scan();
    onRefresh();
  };
  const markRead = async () => {
    await api.readAlerts();
    onRefresh();
  };

  const hot = state
    ? [...state.watchlist.crypto, ...state.watchlist.stocks].filter(
        (r) => r.status !== "watch"
      )
    : [];
  const alerts = state?.alerts.slice(0, 8) ?? [];

  return (
    <>
      <div className="row section">
        <button className="btn" onClick={startScan} disabled={state?.scanning}>
          {state?.scanning ? "Scansione in corso…" : "Scansiona ora"}
        </button>
        {state?.scanning && <span className="scanline">{state.progress}</span>}
        {!state?.scanning && state?.last_scan && (
          <span className="muted">
            Ultima scansione: {new Date(state.last_scan).toLocaleString("it-IT")}
          </span>
        )}
        {state?.last_error && <span className="neg">Errore: {state.last_error}</span>}
      </div>

      <div className="grid grid-2 section">
        <RegimeCard title="Regime Azioni (SPY · QQQ · VIX)" regime={state?.regimes?.stocks} />
        <RegimeCard title="Regime Crypto (BTC)" regime={state?.regimes?.crypto} />
      </div>

      <div className="card section">
        <h3>Situazioni calde (near / triggered)</h3>
        {hot.length > 0 ? (
          <WatchTable rows={hot} onPlan={onPlan} />
        ) : (
          <div className="empty">Nessuna situazione attiva. Pazienza è una posizione.</div>
        )}
      </div>

      <div className="card section">
        <div className="row">
          <h3>Alert recenti</h3>
          <div className="spacer" />
          {(state?.unread_alerts ?? 0) > 0 && (
            <button className="btn small secondary" onClick={markRead}>
              Segna come letti
            </button>
          )}
        </div>
        {alerts.length === 0 && <div className="empty">Nessun alert.</div>}
        {alerts.map((a) => (
          <div key={a.id} className={`alert-item ${a.read ? "" : "unread"}`}>
            <div>
              <strong>{a.symbol}</strong> <span className="muted">({a.market})</span> — {a.message}
            </div>
            <div className="when">{new Date(a.created_at).toLocaleString("it-IT")}</div>
          </div>
        ))}
      </div>
    </>
  );
}
