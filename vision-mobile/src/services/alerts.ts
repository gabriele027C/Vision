/** Alert in-app + notifiche Telegram (bot gratuito creato con @BotFather). */
import { addAlert, getSettings } from "../db/database";

export async function sendTelegram(
  token: string,
  chatId: string,
  text: string
): Promise<boolean> {
  if (!token || !chatId) return false;
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 15_000);
    try {
      const resp = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chatId, text, parse_mode: "HTML" }),
        signal: ctrl.signal,
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      return true;
    } finally {
      clearTimeout(timer);
    }
  } catch (exc) {
    console.warn("invio Telegram fallito:", exc);
    return false;
  }
}

/** Registra l'alert nel DB e, se configurato, lo invia anche su Telegram. */
export function notify(market: string, symbol: string, message: string): void {
  addAlert(market, symbol, message);
  const s = getSettings();
  void sendTelegram(
    s.telegram_token,
    s.telegram_chat_id,
    `<b>Vision TVS</b> — ${symbol} (${market})\n${message}`
  );
}
