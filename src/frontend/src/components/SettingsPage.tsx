import { useEffect, useState } from "react";
import { api } from "../api";
import type { Settings } from "../types";

export default function SettingsPage() {
  const [s, setS] = useState<Settings | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    api.settings().then(setS);
  }, []);

  if (!s) return <div className="empty">Caricamento…</div>;

  const save = async () => {
    setMsg(null);
    try {
      const updated = await api.saveSettings(s);
      setS(updated);
      setMsg("Impostazioni salvate.");
    } catch (e) {
      setMsg((e as Error).message);
    }
  };

  const testTg = async () => {
    setMsg(null);
    try {
      await api.testTelegram();
      setMsg("Messaggio di test inviato su Telegram.");
    } catch (e) {
      setMsg((e as Error).message);
    }
  };

  return (
    <div className="grid grid-2">
      <div className="card">
        <h3>Capitale e rischio (§7 della strategia)</h3>
        <label className="field">
          Capitale del conto (€/$)
          <input
            type="number"
            value={s.capital}
            onChange={(e) => setS({ ...s, capital: parseFloat(e.target.value) || 0 })}
          />
        </label>
        <label className="field">
          Rischio per trade (%) — 1% standard, 0.5% nei primi 20 trade reali o in drawdown &gt;10%
          <input
            type="number" step="0.1" min="0.1" max="2"
            value={s.risk_pct}
            onChange={(e) => setS({ ...s, risk_pct: parseFloat(e.target.value) || 1 })}
          />
        </label>
        <label className="field">
          Intervallo scansione automatica (minuti)
          <input
            type="number" min="5" max="240"
            value={s.scan_interval_min}
            onChange={(e) => setS({ ...s, scan_interval_min: parseInt(e.target.value) || 30 })}
          />
        </label>
      </div>

      <div className="card">
        <h3>Notifiche Telegram (gratuito)</h3>
        <div className="muted" style={{ marginBottom: 12 }}>
          1) Su Telegram cerca <strong>@BotFather</strong> → /newbot → copia il token.<br />
          2) Scrivi un messaggio al tuo bot, poi apri{" "}
          <code>api.telegram.org/bot&lt;TOKEN&gt;/getUpdates</code> e copia il{" "}
          <code>chat.id</code>.
        </div>
        <label className="field">
          Bot token
          <input
            value={s.telegram_token}
            onChange={(e) => setS({ ...s, telegram_token: e.target.value.trim() })}
            placeholder="123456:ABC-..."
          />
        </label>
        <label className="field">
          Chat ID
          <input
            value={s.telegram_chat_id}
            onChange={(e) => setS({ ...s, telegram_chat_id: e.target.value.trim() })}
            placeholder="es. 123456789"
          />
        </label>
        <div className="row">
          <button className="btn" onClick={save}>Salva impostazioni</button>
          <button className="btn secondary" onClick={testTg}>Test Telegram</button>
        </div>
        {msg && <div style={{ marginTop: 10 }} className={msg.includes("salvat") || msg.includes("inviato") ? "pos" : "neg"}>{msg}</div>}
      </div>
    </div>
  );
}
