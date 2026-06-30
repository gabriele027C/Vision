import { useCallback, useEffect, useState } from "react";
import {
  CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api } from "../api";
import type { Metrics, Trade } from "../types";
import { tvUrl } from "./WatchTable";

function Stat({ label, value, suffix }: { label: string; value: string | number | null; suffix?: string }) {
  return (
    <div className="card">
      <h3>{label}</h3>
      <div className="big mono">{value ?? "—"}{value !== null && suffix ? suffix : ""}</div>
    </div>
  );
}

export default function Journal() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [closing, setClosing] = useState<Trade | null>(null);
  const [exitPrice, setExitPrice] = useState("");
  const [mistake, setMistake] = useState(false);
  const [notes, setNotes] = useState("");

  const refresh = useCallback(async () => {
    const [t, m] = await Promise.all([api.trades(), api.metrics()]);
    setTrades(t);
    setMetrics(m);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const submitClose = async () => {
    if (!closing) return;
    await api.closeTrade(closing.id, parseFloat(exitPrice), mistake, notes);
    setClosing(null);
    setExitPrice("");
    setMistake(false);
    setNotes("");
    refresh();
  };

  const removeTrade = async (id: number) => {
    if (confirm("Eliminare questo trade dal journal?")) {
      await api.deleteTrade(id);
      refresh();
    }
  };

  return (
    <>
      <div className="grid grid-4 section">
        <Stat label="Win rate" value={metrics?.win_rate ?? null} suffix="%" />
        <Stat label="Expectancy (R/trade)" value={metrics?.expectancy ?? null} />
        <Stat label="Profit factor" value={metrics?.profit_factor ?? null} />
        <Stat label="Max drawdown (R)" value={metrics?.max_drawdown_r ?? null} />
      </div>

      <div className="card section">
        <h3>
          Validazione demo: {metrics?.closed_trades ?? 0} / {metrics?.validation_target ?? 50} trade chiusi
          {metrics?.validation_passed && " — SUPERATA (puoi passare al reale a rischio 0.5%)"}
        </h3>
        <div className="progress-track">
          <div className="progress-fill" style={{ width: `${metrics?.validation_progress_pct ?? 0}%` }} />
        </div>
        <div className="muted" style={{ marginTop: 8 }}>
          Soglie per passare al capitale reale: expectancy &gt; 0.15R · profit factor &gt; 1.4 · 50 trade.
          Errori di esecuzione segnati: {metrics?.mistakes ?? 0}.
        </div>
      </div>

      {metrics && metrics.equity_curve.length > 1 && (
        <div className="card section">
          <h3>Curva di equity (R cumulato)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={metrics.equity_curve}>
              <CartesianGrid stroke="#232d42" strokeDasharray="3 3" />
              <XAxis dataKey="trade" stroke="#8b96ab" fontSize={11} />
              <YAxis stroke="#8b96ab" fontSize={11} />
              <Tooltip
                contentStyle={{ background: "#121826", border: "1px solid #232d42", borderRadius: 8 }}
                labelFormatter={(l) => `Trade #${l}`}
              />
              <ReferenceLine y={0} stroke="#8b96ab" />
              <Line type="monotone" dataKey="cum_r" stroke="#4f8cff" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <h3>Trade ({trades.length})</h3>
        {trades.length === 0 && <div className="empty">Nessun trade registrato. Usa il Trade Planner.</div>}
        {trades.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Aperto</th><th>Asset</th><th>Dir</th><th>Setup</th>
                <th>Entrata</th><th>Stop</th><th>Size</th><th>Stato</th><th>R</th><th></th>
              </tr>
            </thead>
            <tbody>
              {trades.map((t) => (
                <tr key={t.id}>
                  <td className="muted">{new Date(t.opened_at).toLocaleDateString("it-IT")}</td>
                  <td>
                    <a
                      className="ticker-link"
                      href={tvUrl(t.market, t.symbol)}
                      target="_blank"
                      rel="noopener noreferrer"
                      title={`Apri ${t.symbol} su TradingView`}
                    >
                      {t.symbol}
                    </a>{" "}
                    {t.mistake ? "⚠️" : ""}
                  </td>
                  <td><span className={`badge ${t.direction}`}>{t.direction}</span></td>
                  <td>{t.setup}</td>
                  <td className="mono">{t.entry_price}</td>
                  <td className="mono">{t.stop_price}</td>
                  <td className="mono">{t.size}</td>
                  <td>
                    <span className={`badge ${t.status === "open" ? "near" : "watch"}`}>{t.status}</span>
                  </td>
                  <td className={`mono ${t.r_result === null ? "" : t.r_result > 0 ? "pos" : "neg"}`}>
                    {t.r_result === null ? "—" : `${t.r_result > 0 ? "+" : ""}${t.r_result}R`}
                  </td>
                  <td>
                    <div className="row" style={{ gap: 6 }}>
                      {t.status === "open" && (
                        <button className="btn small" onClick={() => { setClosing(t); setExitPrice(""); }}>
                          Chiudi
                        </button>
                      )}
                      <button className="btn small danger" onClick={() => removeTrade(t.id)}>×</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {closing && (
        <div className="modal-overlay" onClick={() => setClosing(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Chiudi {closing.symbol} ({closing.direction})</h2>
            <label className="field">
              Prezzo di uscita
              <input type="number" step="any" value={exitPrice} onChange={(e) => setExitPrice(e.target.value)} autoFocus />
            </label>
            <label className="field">
              Note (cosa ha funzionato / cosa no)
              <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
            </label>
            <label className="field" style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <input type="checkbox" style={{ width: "auto", marginTop: 0 }} checked={mistake} onChange={(e) => setMistake(e.target.checked)} />
              Ho violato una regola della strategia in questo trade
            </label>
            <div className="row" style={{ marginTop: 12 }}>
              <button className="btn" disabled={!(parseFloat(exitPrice) > 0)} onClick={submitClose}>
                Conferma chiusura
              </button>
              <button className="btn secondary" onClick={() => setClosing(null)}>Annulla</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
