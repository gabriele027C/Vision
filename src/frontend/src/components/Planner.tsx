import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { AppState, Sizing, WatchRow } from "../types";

// Copy checklist: aggiornamento linguaggio in FASE 7 (ancora riferimenti regime/semaforo).
const CHECKLIST = [
  "Il regime (semaforo) consente questa direzione?",
  "L'asset è nel top/bottom 20% di forza relativa?",
  "Setup A o B completo su Daily? (non \"quasi\")",
  "Trigger confermato su 4H con volume?",
  "Stop definito e distanza ≤ 2.5 ATR?",
  "Rischio aperto totale dopo questo trade ≤ 4%?",
  "Niente earnings/eventi macro nelle prossime 48h?",
  "(Crypto) Funding non estremo? Non è weekend?",
  "Ordine stop REALE pronto da inserire insieme all'entrata su TradingView?",
];

function patternFromSetup(setup: "A" | "B"): string {
  return setup === "A" ? "pullback" : "compression";
}

function findWatchRow(state: AppState | null, market: string, symbol: string): WatchRow | null {
  if (!state) return null;
  const list = market === "crypto" ? state.watchlist.crypto : state.watchlist.stocks;
  return list.find((r) => r.symbol === symbol) ?? null;
}

export default function Planner({
  prefill,
  state,
}: {
  prefill: WatchRow | null;
  state: AppState | null;
}) {
  const [symbol, setSymbol] = useState(prefill?.symbol ?? "");
  const [market, setMarket] = useState(prefill?.market ?? "crypto");
  const [direction, setDirection] = useState(prefill?.direction ?? "long");
  const [setup, setSetup] = useState(prefill?.setup ?? "A");
  const [entry, setEntry] = useState(prefill ? String(prefill.entry_trigger) : "");
  const [stop, setStop] = useState(prefill ? String(prefill.stop) : "");
  const [timeframe, setTimeframe] = useState(prefill?.entry_tf ?? "D");
  const [pattern, setPattern] = useState(patternFromSetup(prefill?.setup ?? "A"));
  const [fundingAtEntry, setFundingAtEntry] = useState(
    prefill?.funding != null ? String(prefill.funding) : ""
  );
  const [rvolAtEntry, setRvolAtEntry] = useState(prefill ? String(prefill.rvol) : "");
  const [oiAtEntry, setOiAtEntry] = useState(
    prefill?.oi_delta_24h != null ? String(prefill.oi_delta_24h) : ""
  );
  const [cvdSlope, setCvdSlope] = useState(
    prefill?.cvd_slope != null ? String(prefill.cvd_slope) : ""
  );
  const [sizing, setSizing] = useState<Sizing | null>(null);
  const [sizingError, setSizingError] = useState<string | null>(null);
  const [checks, setChecks] = useState<boolean[]>(CHECKLIST.map(() => false));
  const [saved, setSaved] = useState<string | null>(null);

  const halfSize = useMemo(() => {
    const regime = state?.regimes?.[market];
    return regime?.half_size ?? false;
  }, [state, market]);

  useEffect(() => {
    if (prefill) {
      setSymbol(prefill.symbol);
      setMarket(prefill.market);
      setDirection(prefill.direction);
      setSetup(prefill.setup);
      setEntry(String(prefill.entry_trigger));
      setStop(String(prefill.stop));
      setTimeframe(prefill.entry_tf ?? "D");
      setPattern(patternFromSetup(prefill.setup));
      setFundingAtEntry(prefill.funding != null ? String(prefill.funding) : "");
      setRvolAtEntry(String(prefill.rvol));
      setOiAtEntry(prefill.oi_delta_24h != null ? String(prefill.oi_delta_24h) : "");
      setCvdSlope(prefill.cvd_slope != null ? String(prefill.cvd_slope) : "");
      setChecks(CHECKLIST.map(() => false));
      setSaved(null);
    }
  }, [prefill]);

  // Se l'utente cambia simbolo, riallinea snapshot dalla watchlist (override restano editabili).
  useEffect(() => {
    const row = findWatchRow(state, market, symbol);
    if (!row) return;
    setTimeframe((prev) => prev || row.entry_tf || "D");
    setFundingAtEntry((prev) => (prev !== "" ? prev : row.funding != null ? String(row.funding) : ""));
    setRvolAtEntry((prev) => (prev !== "" ? prev : String(row.rvol)));
    setOiAtEntry((prev) =>
      prev !== "" ? prev : row.oi_delta_24h != null ? String(row.oi_delta_24h) : ""
    );
    setCvdSlope((prev) => (prev !== "" ? prev : row.cvd_slope != null ? String(row.cvd_slope) : ""));
  }, [state, market, symbol]);

  useEffect(() => {
    const e = parseFloat(entry);
    const s = parseFloat(stop);
    if (!(e > 0) || !(s > 0) || e === s) {
      setSizing(null);
      return;
    }
    let cancelled = false;
    const funding =
      market === "crypto"
        ? state?.watchlist?.crypto?.find((r) => r.symbol === symbol)?.funding ?? null
        : null;
    api
      .sizing(e, s, halfSize, {
        direction,
        market,
        funding_est: funding,
        days_held_est: market === "crypto" ? 3 : 0,
      })
      .then((r) => !cancelled && (setSizing(r), setSizingError(null)))
      .catch((err) => !cancelled && (setSizing(null), setSizingError(err.message)));
    return () => {
      cancelled = true;
    };
  }, [entry, stop, halfSize, direction, market, symbol, state]);

  const allChecked = checks.every(Boolean);
  const target2r = sizing
    ? direction === "long"
      ? (sizing.target_2r_net_long ?? sizing.target_2r_long)
      : (sizing.target_2r_net_short ?? sizing.target_2r_short)
    : null;
  const currentFunding =
    market === "crypto"
      ? state?.watchlist?.crypto?.find((r) => r.symbol === symbol)?.funding ?? null
      : null;

  const parseOpt = (s: string): number | null => {
    if (s.trim() === "") return null;
    const n = parseFloat(s);
    return Number.isFinite(n) ? n : null;
  };

  const registerTrade = async () => {
    if (!sizing) return;
    await api.createTrade({
      symbol,
      market,
      direction,
      setup,
      entry_price: parseFloat(entry),
      stop_price: parseFloat(stop),
      size: sizing.size_units,
      risk_amount: sizing.risk_amount,
      notes: `Pianificato dal Planner. Target 2R: ${target2r}`,
      timeframe,
      pattern,
      funding_at_entry: parseOpt(fundingAtEntry),
      rvol_at_entry: parseOpt(rvolAtEntry),
      oi_at_entry: parseOpt(oiAtEntry),
      cvd_slope_at_entry: parseOpt(cvdSlope),
      scenario_ids: prefill?.scenario_ids ?? [],
    });
    setSaved(`${symbol} registrato nel journal come trade aperto.`);
  };

  return (
    <div className="grid grid-2">
      <div className="card">
        <h3>Parametri del trade</h3>
        <label className="field">
          Simbolo
          <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="es. BTCUSDT / NVDA" />
        </label>
        <div className="grid grid-3">
          <label className="field">
            Mercato
            <select value={market} onChange={(e) => setMarket(e.target.value as "crypto" | "stocks")}>
              <option value="crypto">Crypto</option>
              <option value="stocks">Azioni</option>
            </select>
          </label>
          <label className="field">
            Direzione
            <select value={direction} onChange={(e) => setDirection(e.target.value as "long" | "short")}>
              <option value="long">Long</option>
              <option value="short">Short</option>
            </select>
          </label>
          <label className="field">
            Setup
            <select
              value={setup}
              onChange={(e) => {
                const s = e.target.value as "A" | "B";
                setSetup(s);
                setPattern(patternFromSetup(s));
              }}
            >
              <option value="A">A — Pullback</option>
              <option value="B">B — Breakout</option>
            </select>
          </label>
        </div>
        <div className="grid grid-2">
          <label className="field">
            Prezzo di entrata (livello di rottura)
            <input type="number" step="any" value={entry} onChange={(e) => setEntry(e.target.value)} />
          </label>
          <label className="field">
            Invalidazione
            <input type="number" step="any" value={stop} onChange={(e) => setStop(e.target.value)} />
          </label>
        </div>

        <h3 style={{ marginTop: 12 }}>Snapshot at-entry (journal)</h3>
        <p className="muted" style={{ marginBottom: 8 }}>
          Auto da watchlist; editabili. OI/CVD si popolano con FASE 4.
        </p>
        <div className="grid grid-3">
          <label className="field">
            Timeframe
            <select value={timeframe} onChange={(e) => setTimeframe(e.target.value)}>
              <option value="D">D</option>
              <option value="4H">4H</option>
              <option value="1H">1H</option>
              <option value="15m">15m</option>
            </select>
          </label>
          <label className="field">
            Pattern
            <select value={pattern} onChange={(e) => setPattern(e.target.value)}>
              <option value="pullback">pullback</option>
              <option value="compression">compression</option>
              <option value="breakout">breakout</option>
              <option value="discrezionale">discrezionale</option>
            </select>
          </label>
          <label className="field">
            RVOL
            <input type="number" step="any" value={rvolAtEntry} onChange={(e) => setRvolAtEntry(e.target.value)} />
          </label>
        </div>
        <div className="grid grid-3">
          <label className="field">
            Funding
            <input type="number" step="any" value={fundingAtEntry} onChange={(e) => setFundingAtEntry(e.target.value)} placeholder="es. 0.0001" />
          </label>
          <label className="field">
            OI Δ24h (frazione)
            <input type="number" step="any" value={oiAtEntry} onChange={(e) => setOiAtEntry(e.target.value)} placeholder="es. 0.05" />
          </label>
          <label className="field">
            CVD slope
            <input type="number" step="any" value={cvdSlope} onChange={(e) => setCvdSlope(e.target.value)} />
          </label>
        </div>

        {halfSize && (
          <div className="muted" style={{ color: "var(--yellow)", marginBottom: 10 }}>
            Regime misto: rischio dimezzato automaticamente (contesto informativo).
          </div>
        )}
        {sizingError && (
          <div className="neg" style={{ marginBottom: 10 }}>
            Blocco sizing: {sizingError}
          </div>
        )}

        {sizing && (
          <div className="grid grid-2" style={{ marginTop: 8 }}>
            <div className="card" style={{ background: "var(--bg)" }}>
              <h3>Size per rischio {sizing.half_size ? "0.5%" : "1%"}</h3>
              <div className="big mono">{sizing.size_units}</div>
              <div className="muted">unità · nozionale ≈ {sizing.notional.toLocaleString("it-IT")} $</div>
              <div className="mono" style={{ marginTop: 8 }}>
                Leva implicita: {sizing.leverage ?? "—"}x
                {sizing.leverage_capped ? " (cappata)" : ""}
              </div>
              {market === "crypto" && (
                <div className="mono">
                  Liquidazione stimata: {sizing.liq_price ?? "—"}
                  {sizing.liq_safe === false ? " — BLOCCATA" : ""}
                </div>
              )}
            </div>
            <div className="card" style={{ background: "var(--bg)" }}>
              <h3>Rischio / costi</h3>
              <div className="mono">Rischio: {sizing.risk_amount} $</div>
              <div className="mono">Distanza invalidazione: {sizing.stop_distance_pct}%</div>
              <div className="mono">Costi RT: {sizing.round_trip_cost ?? "—"} $ ({sizing.cost_r ?? "—"} R)</div>
              <div className="mono">2R netto dopo costi: {sizing.net_2r_after_costs ?? "—"} R</div>
              <div className="mono">Target 2R netto: {target2r}</div>
              {market === "crypto" && (
                <div className="mono">
                  Funding corrente:{" "}
                  {currentFunding == null ? "n/d" : `${(currentFunding * 100).toFixed(4)}% / 8h`}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h3>Checklist pre-trade (§12) — una casella vuota = niente trade</h3>
        <div className="checklist">
          {CHECKLIST.map((item, i) => (
            <label key={i}>
              <input
                type="checkbox"
                checked={checks[i]}
                onChange={() => setChecks((c) => c.map((v, j) => (j === i ? !v : v)))}
              />
              {item}
            </label>
          ))}
        </div>
        <div className="row" style={{ marginTop: 16 }}>
          <button
            className="btn"
            disabled={!allChecked || !sizing || !!sizingError || sizing?.liq_safe === false || !symbol}
            onClick={registerTrade}
          >
            Registra trade aperto nel journal
          </button>
          {!allChecked && <span className="muted">Completa la checklist per sbloccare.</span>}
          {(!!sizingError || sizing?.liq_safe === false) && (
            <span className="neg">Registrazione bloccata: sizing non sicuro (liquidazione).</span>
          )}
        </div>
        {saved && <div className="pos" style={{ marginTop: 10 }}>{saved}</div>}
        <div className="muted" style={{ marginTop: 14 }}>
          Flusso: 1) verifica il grafico su TradingView → 2) inserisci l'ordine paper con questi
          valori → 3) registra qui il trade per il journal.
        </div>
      </div>
    </div>
  );
}
