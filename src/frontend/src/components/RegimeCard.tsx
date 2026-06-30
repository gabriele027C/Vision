import type { Regime } from "../types";

const MODE_LABEL: Record<string, string> = {
  long: "Long consentiti",
  short: "Short consentiti",
  mixed: "Misto — size dimezzata",
  halt: "STOP — nessuna nuova posizione",
};

export default function RegimeCard({ title, regime }: { title: string; regime?: Regime }) {
  if (!regime) {
    return (
      <div className="card">
        <h3>{title}</h3>
        <div className="muted">In attesa della prima scansione…</div>
      </div>
    );
  }
  const detail = Object.entries(regime.detail)
    .map(([k, v]) => `${k}: ${typeof v === "number" ? v.toFixed(1) : v ?? "n/d"}`)
    .join(" · ");
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="regime">
        <div className={`light ${regime.mode}`} />
        <div>
          <div className="regime-mode">{MODE_LABEL[regime.mode] ?? regime.mode}</div>
          <div className="regime-detail">{detail}</div>
        </div>
      </div>
    </div>
  );
}
