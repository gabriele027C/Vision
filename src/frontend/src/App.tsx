import { useCallback, useEffect, useState } from "react";
import { api } from "./api";
import type { AppState, WatchRow } from "./types";
import Dashboard from "./components/Dashboard";
import Watchlist from "./components/Watchlist";
import Planner from "./components/Planner";
import Journal from "./components/Journal";
import SettingsPage from "./components/SettingsPage";
import DiagnosticsPanel from "./components/DiagnosticsPanel";

type Tab = "dashboard" | "watchlist" | "diagnostics" | "planner" | "journal" | "settings";

const TABS: { id: Tab; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "watchlist", label: "Watchlist" },
  { id: "diagnostics", label: "Diagnostica" },
  { id: "planner", label: "Trade Planner" },
  { id: "journal", label: "Journal" },
  { id: "settings", label: "Impostazioni" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const [state, setState] = useState<AppState | null>(null);
  const [planned, setPlanned] = useState<WatchRow | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setState(await api.state());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 20_000);
    return () => clearInterval(id);
  }, [refresh]);

  const planTrade = (row: WatchRow) => {
    setPlanned(row);
    setTab("planner");
  };

  return (
    <>
      <header className="header">
        <div className="logo">
          Vision <span>TVS</span>
          <div className="muted" style={{ fontWeight: 400 }}>
            Trend · Volume · Struttura — swing D/4H
          </div>
        </div>
        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`tab ${tab === t.id ? "active" : ""}`}
              onClick={() => setTab(t.id)}
            >
              {t.label}
              {t.id === "dashboard" && (state?.unread_alerts ?? 0) > 0 && (
                <span className="badge-dot" />
              )}
            </button>
          ))}
        </nav>
      </header>

      {error && (
        <div className="card section" style={{ borderColor: "var(--red)" }}>
          Backend non raggiungibile: {error}. Avvia <code>uvicorn main:app</code> in{" "}
          <code>src/backend</code>.
        </div>
      )}

      {tab === "dashboard" && <Dashboard state={state} onRefresh={refresh} onPlan={planTrade} />}
      {tab === "watchlist" && <Watchlist state={state} onPlan={planTrade} />}
      {tab === "diagnostics" && <DiagnosticsPanel state={state} />}
      {tab === "planner" && <Planner prefill={planned} state={state} />}
      {tab === "journal" && <Journal />}
      {tab === "settings" && <SettingsPage />}
    </>
  );
}
