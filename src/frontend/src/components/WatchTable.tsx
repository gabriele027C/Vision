import type { WatchRow } from "../types";

/** Formato prezzi stile trading: punto decimale, niente migliaia IT
 *  (64841 → "64841.80", non "64.841,8"). */
function fmt(x: number): string {
  if (x == null || Number.isNaN(x)) return "—";
  const ax = Math.abs(x);
  if (ax >= 1000) return x.toFixed(2);
  if (ax >= 1) return x.toFixed(2);
  if (ax >= 0.01) return x.toFixed(4);
  return x.toPrecision(4);
}

function alignedTiming(r: WatchRow): string | null {
  const hit = r.timing?.find((t) => t.aligned_with_daily);
  return hit?.timeframe ?? null;
}

function timingTitle(r: WatchRow): string {
  const parts: string[] = [`Ingresso watchlist: ${r.entry_tf ?? "D"}`];
  if (r.tf_4h?.squeeze) parts.push(`4H squeeze: ${r.tf_4h.note ?? "sì"}`);
  for (const t of r.timing ?? []) {
    parts.push(t.note);
  }
  return parts.join("\n");
}

function confluenceTitle(r: WatchRow): string {
  const bd = r.confluence_breakdown;
  if (!bd) return `Confluence ${r.confluence ?? "—"}`;
  const lines = Object.entries(bd).map(([k, v]) => {
    if (v.status === "n/d") return `${k}: n/d`;
    return `${k}: ${v.contrib ?? "—"} (raw ${v.raw})`;
  });
  if (r.confluence_renorm) lines.push("(rinormalizzato su componenti disponibili)");
  return `Confluence ${r.confluence}\n` + lines.join("\n");
}

export function tvUrl(market: string, symbol: string): string {
  // Crypto: perpetual Binance (PREZZO = futures). Azioni: TV usa il punto (BRK.B).
  const tvSymbol =
    market === "crypto" ? `BINANCE:${symbol}.P` : symbol.replace("-", ".");
  return `https://www.tradingview.com/chart/?symbol=${encodeURIComponent(tvSymbol)}&interval=D`;
}

export default function WatchTable({
  rows,
  market = "crypto",
  onPlan,
}: {
  rows: WatchRow[];
  market?: "crypto" | "stocks";
  onPlan: (row: WatchRow) => void;
}) {
  if (rows.length === 0) {
    const emptyMsg =
      market === "crypto"
        ? "Nessun setup valido al momento."
        : "Nessun setup valido al momento. Il mercato riapre domani.";
    return <div className="empty">{emptyMsg}</div>;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>Asset</th>
          <th>TF</th>
          <th>Conf</th>
          <th>Dir</th>
          <th>Setup</th>
          <th>Stato</th>
          <th>RS</th>
          <th>RVOL</th>
          <th>OI</th>
          <th>CVD</th>
          <th>Prezzo</th>
          <th>Rottura</th>
          <th>Invalidazione</th>
          <th>Funding</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={`${r.market}-${r.symbol}-${r.direction}`} title={r.note}>
            <td>
              <a
                className="ticker-link"
                href={tvUrl(r.market, r.symbol)}
                target="_blank"
                rel="noopener noreferrer"
                title={`Apri ${r.symbol} su TradingView`}
              >
                {r.symbol}
              </a>
              {r.warnings.length > 0 && (
                <span title={r.warnings.join("\n")} style={{ marginLeft: 6 }}>⚠️</span>
              )}
            </td>
            <td>
              <span className="badge setup" title={timingTitle(r)}>
                {r.entry_tf ?? "D"}
                {alignedTiming(r) ? ` · ${alignedTiming(r)}` : ""}
              </span>
            </td>
            <td className="mono" title={confluenceTitle(r)}>
              {r.confluence != null ? r.confluence.toFixed(0) : "—"}
            </td>
            <td><span className={`badge ${r.direction}`}>{r.direction}</span></td>
            <td>
              <span className="badge setup">Setup {r.setup}</span>
              {(r.scenario_ids?.length ?? 0) > 0 && (
                <div style={{ marginTop: 4 }}>
                  {r.scenario_ids!.slice(0, 3).map((id) => (
                    <span key={id} className="badge watch" style={{ marginRight: 4, fontSize: 10 }} title={id}>
                      {id}
                    </span>
                  ))}
                </div>
              )}
            </td>
            <td><span className={`badge ${r.status}`}>
              {r.status === "blocked" ? "veto funding" : r.status}
            </span></td>
            <td className="mono">{(r.rs_score * 100).toFixed(0)}%</td>
            <td className="mono">{r.rvol.toFixed(2)}</td>
            <td className="mono" title={r.oi_delta_24h != null ? `Δ24h ${(r.oi_delta_24h * 100).toFixed(2)}%` : undefined}>
              {r.oi_arrow ?? "—"}
            </td>
            <td className="mono" title={r.cvd_slope != null ? `slope ${r.cvd_slope}` : undefined}>
              {r.cvd_arrow ?? "—"}
            </td>
            <td
              className="mono"
              title={
                r.price_asof
                  ? `Aggiornato ${new Date(r.price_asof).toLocaleString("it-IT")}${r.price_live ? " (live)" : ""}`
                  : r.price_source
                    ? `Fonte: ${r.price_source}`
                    : "Prezzo allo scan"
              }
            >
              {fmt(r.last_price)}
            </td>
            <td className="mono">{fmt(r.entry_trigger)}</td>
            <td className="mono">{fmt(r.stop)}</td>
            <td className="mono">
              {r.funding !== null ? `${(r.funding * 100).toFixed(3)}%` : "—"}
            </td>
            <td>
              {r.status === "blocked" ? (
                <button className="btn small" disabled title="Funding estremo: non operabile">
                  Bloccato
                </button>
              ) : (
                <button className="btn small" onClick={() => onPlan(r)}>Pianifica</button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
