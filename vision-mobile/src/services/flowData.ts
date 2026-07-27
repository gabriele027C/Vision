/** Costruisce snapshot flusso da REST Binance — speculare a services/flow_data.py. */
import * as binanceClient from "../data/binanceClient";
import {
  buildFlowSnapshot,
  cvdSlopeNormalized,
  oiDeltasFromHist,
  priceDeltaPct,
  type FlowSnapshot,
} from "../engine/flow";
import type { WatchRow } from "../engine/types";

export async function fetchFlowSnapshot(symbol: string): Promise<FlowSnapshot> {
  const oiHist = await binanceClient.openInterestHist(symbol, "4h", 30);
  const deltas = oiDeltasFromHist(oiHist.map((p) => p.sumOpenInterest), 6);

  const fut = await binanceClient.futuresKlines(symbol, "4h", 100);
  // Escludi barra in formazione
  const hist = fut.length > 1 ? fut.slice(0, -1) : [];
  let slope: number | null = null;
  let pxDelta: number | null = null;
  if (hist.length) {
    slope = cvdSlopeNormalized(
      hist.map((b) => b.volume),
      hist.map((b) => b.tbb)
    );
    pxDelta = priceDeltaPct(
      hist.map((b) => b.close),
      6
    );
  }

  return buildFlowSnapshot({
    oi_value: deltas.oi_value,
    oi_delta_24h: deltas.oi_delta_24h,
    oi_delta_3d: deltas.oi_delta_3d,
    cvd_slope: slope,
    price_delta: pxDelta,
  });
}

export async function enrichRowWithFlow(row: WatchRow): Promise<WatchRow> {
  try {
    const snap = await fetchFlowSnapshot(row.symbol);
    row.oi_state = snap.oi_state;
    row.oi_arrow = snap.oi_arrow;
    row.oi_value = snap.oi_value;
    row.oi_delta_24h = snap.oi_delta_24h;
    row.cvd_state = snap.cvd_state;
    row.cvd_arrow = snap.cvd_arrow;
    row.cvd_slope = snap.cvd_slope;
  } catch (exc) {
    console.warn(`[flow] ${row.symbol} fallito:`, exc);
  }
  return row;
}
