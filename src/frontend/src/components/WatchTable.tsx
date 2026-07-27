import type { WatchRow } from "../types";

function fmt(x: number): string {
  if (x >= 1000) return x.toLocaleString("it-IT", { maximumFractionDigits: 2 });
  if (x >= 1) return x.toFixed(2);
  return x.toPrecision(4);
}

export function tvUrl(market: string, symbol: string): string {
  // Crypto: coppie spot Binance. Azioni: TradingView usa il punto (BRK.B), Yahoo il trattino.
  const tvSymbol = market === "crypto" ? `BINANCE:${symbol}` : symbol.replace("-", ".");
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
          <th>Dir</th>
          <th>Setup</th>
          <th>Stato</th>
          <th>RS</th>
          <th>RVOL</th>
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
            <td><span className={`badge ${r.direction}`}>{r.direction}</span></td>
            <td><span className="badge setup">Setup {r.setup}</span></td>
            <td><span className={`badge ${r.status}`}>
              {r.status === "blocked" ? "veto funding" : r.status}
            </span></td>
            <td className="mono">{(r.rs_score * 100).toFixed(0)}%</td>
            <td className="mono">{r.rvol.toFixed(2)}</td>
            <td className="mono">{fmt(r.last_price)}</td>
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
