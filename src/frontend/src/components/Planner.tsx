import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import type { AppState, Sizing, WatchRow } from "../types";

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
      setChecks(CHECKLIST.map(() => false));
      setSaved(null);
    }
  }, [prefill]);

  useEffect(() => {
    const e = parseFloat(entry);
    const s = parseFloat(stop);
    if (!(e > 0) || !(s > 0) || e === s) {
      setSizing(null);
      return;
    }
    let cancelled = false;
    api
      .sizing(e, s, halfSize)
      .then((r) => !cancelled && (setSizing(r), setSizingError(null)))
      .catch((err) => !cancelled && (setSizing(null), setSizingError(err.message)));
    return () => {
      cancelled = true;
    };
  }, [entry, stop, halfSize]);

  const allChecked = checks.every(Boolean);
  const target2r = sizing
    ? direction === "long"
      ? sizing.target_2r_long
      : sizing.target_2r_short
    : null;

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
            <select value={setup} onChange={(e) => setSetup(e.target.value as "A" | "B")}>
              <option value="A">A — Pullback</option>
              <option value="B">B — Breakout</option>
            </select>
          </label>
        </div>
        <div className="grid grid-2">
          <label className="field">
            Prezzo di entrata (trigger)
            <input type="number" step="any" value={entry} onChange={(e) => setEntry(e.target.value)} />
          </label>
          <label className="field">
            Stop loss
            <input type="number" step="any" value={stop} onChange={(e) => setStop(e.target.value)} />
          </label>
        </div>

        {halfSize && (
          <div className="muted" style={{ color: "var(--yellow)", marginBottom: 10 }}>
            Regime misto: rischio dimezzato automaticamente (§2 della strategia).
          </div>
        )}
        {sizingError && <div className="neg">{sizingError}</div>}

        {sizing && (
          <div className="grid grid-2" style={{ marginTop: 8 }}>
            <div className="card" style={{ background: "var(--bg)" }}>
              <h3>Size da inserire su TradingView</h3>
              <div className="big mono">{sizing.size_units}</div>
              <div className="muted">unità · nozionale ≈ {sizing.notional.toLocaleString("it-IT")} $</div>
            </div>
            <div className="card" style={{ background: "var(--bg)" }}>
              <h3>Rischio / livelli</h3>
              <div className="mono">Rischio: {sizing.risk_amount} € ({sizing.half_size ? "0.5%" : "1%"})</div>
              <div className="mono">Distanza stop: {sizing.stop_distance_pct}%</div>
              <div className="mono">Target 2R (chiudi 50%): {target2r}</div>
              <div className="mono">A +1R → stop a breakeven</div>
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
          <button className="btn" disabled={!allChecked || !sizing || !symbol} onClick={registerTrade}>
            Registra trade aperto nel journal
          </button>
          {!allChecked && <span className="muted">Completa la checklist per sbloccare.</span>}
        </div>
        {saved && <div className="pos" style={{ marginTop: 10 }}>{saved}</div>}
        <div className="muted" style={{ marginTop: 14 }}>
          Flusso: 1) verifica il grafico su TradingView → 2) inserisci l'ordine paper con questi
          valori → 3) registra qui il trade per il conteggio dei 50 di validazione.
        </div>
      </div>
    </div>
  );
}
