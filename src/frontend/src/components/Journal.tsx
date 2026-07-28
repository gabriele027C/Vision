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
  const [maeR, setMaeR] = useState("");
  const [mfeR, setMfeR] = useState("");

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
    const mae = maeR.trim() === "" ? null : parseFloat(maeR);
    const mfe = mfeR.trim() === "" ? null : parseFloat(mfeR);
    await api.closeTrade(closing.id, parseFloat(exitPrice), mistake, notes, {
      mae_r: mae != null && Number.isFinite(mae) ? mae : null,
      mfe_r: mfe != null && Number.isFinite(mfe) ? mfe : null,
    });
    setClosing(null);
    setExitPrice("");
    setMistake(false);
    setNotes("");
    setMaeR("");
    setMfeR("");
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
          {" "}Statistiche del journal affidabili da n≥{metrics?.reliable_stats_from_n ?? 100}
          {metrics?.stats_reliable ? " (raggiunte)." : "."}
        </div>
        <div className="muted" style={{ marginTop: 8 }}>
          I breakdown per timeframe / pattern / scenario si popolano con i nuovi trade
          registrati (n≥10 per riga). I trade storici senza quei campi restano esclusi
          dai bucket.
        </div>
      </div>

      {metrics?.random_benchmark && (
        <div className="card section">
          <h3>Confronto col caso (R:R 2:1)</h3>
          <p className="muted" style={{ marginBottom: 8 }}>{metrics.random_benchmark.note}</p>
          <div className="grid grid-4">
            <Stat label="WR tuo" value={metrics.random_benchmark.user_wr_pct} suffix="%" />
            <Stat label="riferimento caso (≈33% a 2R)" value={metrics.random_benchmark.expected_wr_pct} suffix="%" />
            <Stat
              label="Delta (pp)"
              value={metrics.random_benchmark.delta_wr_pp}
              suffix={metrics.random_benchmark.delta_wr_pp != null && metrics.random_benchmark.delta_wr_pp > 0 ? " ▲" : ""}
            />
          </div>
        </div>
      )}

      {/* Sempre visibile: anche se i bucket sono vuoti, la nota spiega perché */}
      <div className="card section">
        <h3>Expectancy per timeframe / pattern / contesto</h3>
        <p className="muted" style={{ marginBottom: 12 }}>
          I breakdown per timeframe/pattern/scenario si popolano con i nuovi trade
          registrati (n≥10 per riga).
        </p>
        <div className="grid grid-2" style={{ gap: 16 }}>
          <div>
            <h4 className="muted">Timeframe</h4>
            {(metrics?.by_timeframe ?? []).length === 0 && <div className="muted">—</div>}
            {(metrics?.by_timeframe ?? []).map((b) => (
              <div key={b.key} className="mono" style={{ marginBottom: 4 }}>
                {b.key}: n={b.n} WR={b.win_rate}% exp={b.expectancy}R
              </div>
            ))}
          </div>
          <div>
            <h4 className="muted">Pattern</h4>
            {(metrics?.by_pattern ?? []).length === 0 && <div className="muted">—</div>}
            {(metrics?.by_pattern ?? []).map((b) => (
              <div key={b.key} className="mono" style={{ marginBottom: 4 }}>
                {b.key}: n={b.n} WR={b.win_rate}% exp={b.expectancy}R
              </div>
            ))}
          </div>
        </div>
        {metrics?.by_context && (
          <div className="grid grid-3" style={{ gap: 16, marginTop: 16 }}>
            {(
              [
                ["RVOL", metrics.by_context.rvol],
                ["Funding", metrics.by_context.funding],
                ["OI", metrics.by_context.oi],
              ] as const
            ).map(([label, buckets]) => (
              <div key={label}>
                <h4 className="muted">{label}</h4>
                {buckets.length === 0 && <div className="muted">—</div>}
                {buckets.map((b) => (
                  <div key={b.key} className="mono" style={{ marginBottom: 4 }}>
                    {b.key}: n={b.n} WR={b.win_rate}% exp={b.expectancy}R
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
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
                <th>Aperto</th><th>Asset</th><th>TF</th><th>Pattern</th><th>Dir</th><th>Setup</th>
                <th>Entrata</th><th>Invalidazione</th><th>Size</th>
                <th>OIΔ</th><th>CVD</th><th>Fund</th><th>RVOL</th>
                <th>Stato</th><th>R</th><th>MAE/MFE</th><th></th>
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
                  <td className="muted">{t.timeframe ?? "—"}</td>
                  <td className="muted">{t.pattern ?? "—"}</td>
                  <td><span className={`badge ${t.direction}`}>{t.direction}</span></td>
                  <td>{t.setup}</td>
                  <td className="mono">{t.entry_price}</td>
                  <td className="mono">{t.stop_price}</td>
                  <td className="mono">{t.size}</td>
                  <td className="mono muted">{t.oi_at_entry ?? "—"}</td>
                  <td className="mono muted">{t.cvd_slope_at_entry ?? "—"}</td>
                  <td className="mono muted">
                    {t.funding_at_entry != null ? (t.funding_at_entry * 100).toFixed(3) + "%" : "—"}
                  </td>
                  <td className="mono muted">{t.rvol_at_entry ?? "—"}</td>
                  <td>
                    <span className={`badge ${t.status === "open" ? "near" : "watch"}`}>{t.status}</span>
                  </td>
                  <td className={`mono ${t.r_result === null ? "" : t.r_result > 0 ? "pos" : "neg"}`}>
                    {t.r_result === null ? "—" : `${t.r_result > 0 ? "+" : ""}${t.r_result}R`}
                  </td>
                  <td className="mono muted">
                    {t.mae_r != null || t.mfe_r != null
                      ? `${t.mae_r ?? "—"} / ${t.mfe_r ?? "—"}`
                      : "—"}
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
            <div className="grid grid-2">
              <label className="field">
                MAE (R, opzionale)
                <input type="number" step="any" value={maeR} onChange={(e) => setMaeR(e.target.value)} />
              </label>
              <label className="field">
                MFE (R, opzionale)
                <input type="number" step="any" value={mfeR} onChange={(e) => setMfeR(e.target.value)} />
              </label>
            </div>
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
