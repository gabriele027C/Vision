"""Alert in-app + notifiche Telegram (bot gratuito creato con @BotFather)."""
import logging

import httpx

import database

log = logging.getLogger(__name__)


def send_telegram(token: str, chat_id: str, text: str) -> bool:
    if not token or not chat_id:
        return False
    try:
        resp = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15.0,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.warning("invio Telegram fallito: %s", exc)
        return False


def notify(market: str, symbol: str, message: str) -> None:
    """Registra l'alert nel DB e, se configurato, lo invia anche su Telegram."""
    database.add_alert(market, symbol, message)
    s = database.get_settings()
    send_telegram(
        s["telegram_token"],
        s["telegram_chat_id"],
        f"<b>Vision TVS</b> — {symbol} ({market})\n{message}",
    )
