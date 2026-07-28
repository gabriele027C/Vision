import { useCallback, useEffect, useMemo, useState } from "react";

import { api } from "../api";

import type { AppState, AssetDiagnostics, FilterResult } from "../types";

import { tvUrl } from "./WatchTable";



function statusIcon(status: FilterResult["status"]) {

  if (status === "pass") return "✓";

  if (status === "fail") return "✗";

  if (status === "warn") return "⚠";

  return "—";

}



function FilterList({ filters }: { filters: FilterResult[] }) {

  return (

    <ul className="diag-filters">

      {filters.map((f) => (

        <li key={f.id} className={`filter-${f.status}`}>

          <span className="diag-icon">{statusIcon(f.status)}</span>

          <div>

            <strong>{f.label}</strong>

            {f.message && <div className="muted diag-msg">{f.message}</div>}

          </div>

        </li>

      ))}

    </ul>

  );

}



function RsBar({ rs }: { rs: number | null }) {

  if (rs === null) return <span className="muted">n/d</span>;

  const pct = rs * 100;

  return (

    <div className="rs-bar-wrap">

      <div className="rs-bar">

        <div className="rs-zone rs-zone-short" title="Bottom 20%" />

        <div className="rs-zone rs-zone-mid" />

        <div className="rs-zone rs-zone-long" title="Top 20%" />

        <div className="rs-marker" style={{ left: `${Math.min(100, Math.max(0, pct))}%` }} />

      </div>

      <span className="mono">{pct.toFixed(0)}%</span>

    </div>

  );

}



function SetupBadge({ ok }: { ok: boolean }) {

  return <span className={ok ? "filter-pass" : "filter-fail"}>{ok ? "✓" : "✗"}</span>;

}



function AssetCard({ asset }: { asset: AssetDiagnostics }) {

  const [open, setOpen] = useState({
    regime: true,
    screener: true,
    flow: true,
    scenarios: true,
    a: false,
    b: false,
  });



  return (

    <div className="card diag-card">

      <div className="row">

        <h3>

          <a

            className="ticker-link"

            href={tvUrl(asset.market, asset.symbol)}

            target="_blank"

            rel="noopener noreferrer"

          >

            {asset.symbol}

          </a>

          {asset.on_watchlist && <span className="badge triggered" style={{ marginLeft: 8 }}>In watchlist</span>}

        </h3>

        <div className="spacer" />

        <span className={`badge ${asset.direction}`}>{asset.direction}</span>

        {asset.best_setup && <span className="badge setup">Setup {asset.best_setup}</span>}

      </div>

      <div className="muted mono" style={{ marginTop: 6, marginBottom: 8, fontSize: 13 }}>
        {asset.price_live ? (
          <>
            Prezzo <strong>live</strong> {asset.last_price != null ? asset.last_price : "—"}
            {asset.price_asof ? ` @ ${new Date(asset.price_asof).toLocaleString("it-IT")}` : ""}
          </>
        ) : (
          <>
            Prezzo <strong>close D</strong> {asset.last_price != null ? asset.last_price : "—"}
            {asset.price_asof || asset.close_d_asof
              ? ` @ ${new Date(asset.price_asof ?? asset.close_d_asof!).toLocaleString("it-IT")}`
              : ""}
          </>
        )}
        {asset.close_d_price != null && asset.price_live && (
          <span style={{ marginLeft: 12 }}>
            · filtri: close D {asset.close_d_price}
            {asset.close_d_asof
              ? ` @ ${new Date(asset.close_d_asof).toLocaleString("it-IT")}`
              : ""}
          </span>
        )}
      </div>



      {asset.blockers.length > 0 && (

        <div className="diag-blockers">

          <strong>Blocker principali</strong>

          <ul>

            {asset.blockers.map((b, i) => (

              <li key={i}>{b}</li>

            ))}

          </ul>

        </div>

      )}



      <div className="diag-section">

        <button type="button" className="diag-toggle" onClick={() => setOpen((o) => ({ ...o, regime: !o.regime }))}>

          1. Regime mercato {open.regime ? "▾" : "▸"}

        </button>

        {open.regime && <FilterList filters={asset.regime_filters} />}

      </div>



      <div className="diag-section">

        <button type="button" className="diag-toggle" onClick={() => setOpen((o) => ({ ...o, screener: !o.screener }))}>

          2. Screener (§3) {open.screener ? "▾" : "▸"}

        </button>

        {open.screener && (

          <>

            <div className="diag-rs-label muted">Forza relativa (percentile — ranking, non gate)</div>

            <RsBar rs={asset.rs_score} />

            <FilterList filters={asset.screener_filters} />

          </>

        )}

      </div>



      {asset.market === "crypto" && (

        <div className="diag-section">

          <button type="button" className="diag-toggle" onClick={() => setOpen((o) => ({ ...o, flow: !o.flow }))}>

            3. Flusso OI/CVD {open.flow ? "▾" : "▸"}

          </button>

          {open.flow && (

            <>

              {asset.flow && (

                <div className="muted" style={{ marginBottom: 8 }}>

                  {asset.flow.combo_label} — {asset.flow.combo_message}

                </div>

              )}

              <FilterList filters={asset.flow_filters ?? []} />

            </>

          )}

        </div>

      )}



      {(asset.scenarios?.length ?? 0) > 0 && (

        <div className="diag-section">

          <button type="button" className="diag-toggle" onClick={() => setOpen((o) => ({ ...o, scenarios: !o.scenarios }))}>

            Scenari attivi ({asset.scenarios!.length}) {open.scenarios ? "▾" : "▸"}

          </button>

          {open.scenarios &&
            asset.scenarios!.map((sc) => (
              <div
                key={sc.id}
                className="card"
                style={{
                  marginTop: 8,
                  borderLeft: sc.lato_operativo ? undefined : "3px solid var(--yellow)",
                }}
              >
                <div className="row" style={{ gap: 8, alignItems: "center" }}>
                  <strong>{sc.titolo}</strong>
                  {!sc.lato_operativo && <span className="badge near">protezione</span>}
                  <span className="muted mono">{sc.id}</span>
                </div>
                <p style={{ marginTop: 8 }}>{sc.lettura}</p>
                <h4 className="muted">Monitorare</h4>
                <ul className="checklist">
                  {sc.monitorare.map((m, i) => (
                    <li key={i}>
                      <label>
                        <input type="checkbox" /> {m}
                      </label>
                    </li>
                  ))}
                </ul>
                <p className="muted"><strong>Invalidazione:</strong> {sc.invalidazione}</p>
                <p className="muted"><strong>Errore tipico:</strong> {sc.errore_tipico}</p>
                <p className="muted" style={{ marginTop: 8, fontSize: 12 }}>{sc.footer}</p>
              </div>
            ))}

        </div>

      )}



      <div className="diag-section">

        <button type="button" className="diag-toggle" onClick={() => setOpen((o) => ({ ...o, a: !o.a }))}>

          {asset.market === "crypto" ? "4" : "3"}. Setup A {asset.setup_a.eligible ? "✓" : "✗"} {open.a ? "▾" : "▸"}

        </button>

        {open.a && <FilterList filters={asset.setup_a.filters} />}

      </div>



      <div className="diag-section">

        <button type="button" className="diag-toggle" onClick={() => setOpen((o) => ({ ...o, b: !o.b }))}>

          {asset.market === "crypto" ? "5" : "4"}. Setup B {asset.setup_b.eligible ? "✓" : "✗"} {open.b ? "▾" : "▸"}

        </button>

        {open.b && <FilterList filters={asset.setup_b.filters} />}

      </div>



      <div className="muted" style={{ marginTop: 12, fontSize: 12 }}>

        Direzione analizzata: <strong>{asset.direction}</strong>

        {asset.suggested_direction && asset.suggested_direction !== asset.direction && (

          <> · naturale RS: {asset.suggested_direction}</>

        )}

        {" · "}

        Candidato screener: {asset.watchlist_eligible ? "sì" : "no"}

      </div>

    </div>

  );

}



export default function DiagnosticsPanel({ state }: { state: AppState | null }) {

  const [market, setMarket] = useState<"crypto" | "stocks">("crypto");

  const [items, setItems] = useState<AssetDiagnostics[]>([]);

  const [selected, setSelected] = useState<string | null>(null);

  const [query, setQuery] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const [sortRs, setSortRs] = useState<"asc" | "desc">("asc");



  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.diagnostics(market);
      setItems(res.items);
      setSelected((prev) => prev ?? (res.items.length > 0 ? res.items[0].symbol : null));
    } catch (e) {
      setError((e as Error).message);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [market]);

  useEffect(() => {
    setSelected(null);
    load();
  }, [market, state?.last_scan, load]);

  const symbols = useMemo(() => items.map((i) => i.symbol).sort(), [items]);

  const sorted = useMemo(() => {

    const copy = [...items];

    copy.sort((a, b) => {

      const ra = a.rs_score ?? 0.5;

      const rb = b.rs_score ?? 0.5;

      return sortRs === "asc" ? ra - rb : rb - ra;

    });

    return copy;

  }, [items, sortRs]);



  const selectedAsset = items.find((i) => i.symbol === selected) ?? null;



  const searchSymbol = async () => {

    const raw = query.trim().toUpperCase();

    if (!raw) return;

    const sym = market === "crypto" && !raw.endsWith("USDT") ? `${raw}USDT` : raw;

    setLoading(true);

    setError(null);

    try {

      const one = await api.diagnosticSymbol(market, sym);

      setItems((prev) => {

        const rest = prev.filter((p) => p.symbol !== one.symbol);

        return [...rest, one];

      });

      setSelected(one.symbol);

    } catch (e) {

      setError((e as Error).message);

    } finally {

      setLoading(false);

    }

  };



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

        <input

          className="diag-search"

          placeholder="Cerca simbolo (es. ETHUSDT, NVDA)"

          value={query}

          onChange={(e) => setQuery(e.target.value)}

          onKeyDown={(e) => e.key === "Enter" && searchSymbol()}

          list="diag-symbols"

        />

        <datalist id="diag-symbols">

          {symbols.map((s) => (

            <option key={s} value={s} />

          ))}

        </datalist>

        <button className="btn small secondary" onClick={searchSymbol} disabled={loading}>

          Cerca

        </button>

        <button className="btn small secondary" onClick={load} disabled={loading}>

          Aggiorna

        </button>

      </div>



      {!state?.last_scan && (

        <div className="card section muted">

          Nessuna scansione ancora — avvia il backend o premi &quot;Scansiona ora&quot; dalla Dashboard.

        </div>

      )}



      {error && <div className="card section neg">{error}</div>}

      {loading && <div className="muted section">Caricamento diagnostica…</div>}



      <div className="grid grid-2 section">

        <div>

          {selectedAsset ? (

            <AssetCard asset={selectedAsset} />

          ) : (

            <div className="card empty">Seleziona un asset dalla tabella o cerca un simbolo.</div>

          )}

        </div>



        <div className="card diag-universe-card">

          <div className="row">

            <h3>Riepilogo universo</h3>

            <div className="spacer" />

            <button

              className="btn small secondary"

              onClick={() => setSortRs((s) => (s === "asc" ? "desc" : "asc"))}

            >

              RS {sortRs === "asc" ? "↑" : "↓"}

            </button>

          </div>

          {sorted.length === 0 ? (

            <div className="empty">Nessun dato diagnostico.</div>

          ) : (

            <div className="diag-universe-scroll">

              <table>

                <thead>

                  <tr>

                    <th>Symbol</th>

                    <th>RS%</th>

                    <th>WL</th>

                    <th>A</th>

                    <th>B</th>

                    <th>Blocker</th>

                  </tr>

                </thead>

                <tbody>

                  {sorted

                    .filter((r) => !query.trim() || r.symbol.includes(query.trim().toUpperCase()))

                    .map((r) => (

                      <tr

                        key={r.symbol}

                        className={r.symbol === selected ? "diag-row-selected" : "diag-row"}

                        onClick={() => setSelected(r.symbol)}

                        style={{ cursor: "pointer" }}

                      >

                        <td className="mono">{r.symbol}</td>

                        <td className="mono">{r.rs_score !== null ? (r.rs_score * 100).toFixed(0) : "—"}</td>

                        <td>{r.on_watchlist ? "✓" : "—"}</td>

                        <td><SetupBadge ok={r.setup_a.eligible} /></td>

                        <td><SetupBadge ok={r.setup_b.eligible} /></td>

                        <td className="muted" style={{ fontSize: 11, maxWidth: 180 }}>

                          {r.blockers[0] ?? (r.on_watchlist ? "In watchlist" : "—")}

                        </td>

                      </tr>

                    ))}

                </tbody>

              </table>

            </div>

          )}

          <div className="muted diag-universe-footer">

            {items.length} asset in cache

            {market === "stocks" ? " (top 30 RS + watchlist)" : " (universo crypto)"}.

          </div>

        </div>

      </div>

    </>

  );

}


