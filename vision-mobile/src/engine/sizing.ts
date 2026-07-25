/** Position sizing frazionale fisso (§7) con vincoli futures — speculare a engine/sizing.py. */
import type { SizingResult } from "./types";

export const CRYPTO_MAX_LEVERAGE = 5.0;
export const STOCKS_MAX_LEVERAGE = 2.0; // margine Reg-T
export const DEFAULT_TAKER_FEE = 0.00055; // 0.055% per lato

function round(x: number, decimals: number): number {
  const f = 10 ** decimals;
  return Math.round(x * f) / f;
}

export function positionSize(
  capital: number,
  riskPct: number,
  entry: number,
  stop: number,
  halfSize = false,
  direction: "long" | "short" | null = null,
  maxLeverage: number | null = null,
  takerFee: number = DEFAULT_TAKER_FEE,
  market: "crypto" | "stocks" = "crypto"
): SizingResult {
  let riskAmount = capital * (riskPct / 100);
  if (halfSize) riskAmount /= 2;
  const distance = Math.abs(entry - stop);
  if (distance <= 0 || entry <= 0) {
    return { error: "Entrata e stop non validi (distanza nulla)" };
  }

  const dir: "long" | "short" = direction ?? (stop < entry ? "long" : "short");
  const levCap =
    maxLeverage ?? (market === "stocks" ? STOCKS_MAX_LEVERAGE : CRYPTO_MAX_LEVERAGE);

  let sizeUnits = riskAmount / distance;
  let notional = sizeUnits * entry;
  const impliedLeverage = capital > 0 ? notional / capital : 0;

  const leverageCapped = impliedLeverage > levCap;
  if (leverageCapped) {
    notional = levCap * capital;
    sizeUnits = notional / entry;
    riskAmount = sizeUnits * distance;
  }

  const leverage = capital > 0 ? notional / capital : 0;

  let liqPrice: number | null = null;
  let liqSafe = true;
  if (market === "crypto" && leverage > 0) {
    if (dir === "long") {
      liqPrice = entry * (1 - 1 / leverage);
      liqSafe = stop > liqPrice;
    } else {
      liqPrice = entry * (1 + 1 / leverage);
      liqSafe = stop < liqPrice;
    }
    if (!liqSafe) {
      return {
        error:
          `Stop (${stop}) oltre il prezzo di liquidazione stimato ` +
          `(${liqPrice.toPrecision(6)}) a leva ${leverage.toFixed(2)}x: la posizione ` +
          `verrebbe liquidata prima dello stop. Riduci la leva o avvicina lo stop.`,
      };
    }
  }

  const roundTripCost = 2 * takerFee * notional;
  const costPerUnit = sizeUnits > 0 ? roundTripCost / sizeUnits : 0;

  return {
    risk_amount: round(riskAmount, 2),
    stop_distance: round(distance, 6),
    stop_distance_pct: round((distance / entry) * 100, 2),
    size_units: round(sizeUnits, 6),
    notional: round(notional, 2),
    half_size: halfSize,
    target_2r_long: round(entry + 2 * distance, 6),
    target_2r_short: round(entry - 2 * distance, 6),
    direction: dir,
    market,
    leverage: round(leverage, 2),
    max_leverage: levCap,
    leverage_capped: leverageCapped,
    liq_price: liqPrice != null ? round(liqPrice, 6) : null,
    liq_safe: liqSafe,
    round_trip_cost: round(roundTripCost, 4),
    target_2r_net_long: round(entry + 2 * distance + costPerUnit, 6),
    target_2r_net_short: round(entry - 2 * distance - costPerUnit, 6),
  };
}
