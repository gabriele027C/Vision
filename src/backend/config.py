"""Configurazione statica dell'app Vision TVS."""
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
CACHE_DIR = BACKEND_DIR / "cache"
DB_PATH = BACKEND_DIR / "vision_app.db"

CACHE_DIR.mkdir(exist_ok=True)

# --- Universo ---
CRYPTO_TOP_N = 50
STABLECOINS = {
    "USDC", "FDUSD", "TUSD", "DAI", "USDP", "PYUSD", "EUR", "EURI",
    "USDE", "BUSD", "UST", "USTC", "AEUR", "XUSD", "USD1", "RLUSD",
    "XAUT", "PAXG",  # token oro: non sono asset crypto direzionali
}
LEVERAGED_SUFFIXES = ("UP", "DOWN", "BULL", "BEAR")
MIN_CRYPTO_QUOTE_VOLUME = 25_000_000  # floor di liquidità; l'universo resta top N per volume

STOCK_MIN_PRICE = 10.0
STOCK_MIN_AVG_VOLUME = 1_000_000
STOCK_MIN_ADR_PCT = 2.0

# --- Strategia (vedi docs/STRATEGIA_SWING.md) ---
RS_TOP_PERCENTILE = 0.80      # long: top 20%
RS_BOTTOM_PERCENTILE = 0.20   # short: bottom 20%
RVOL_INTEREST = 1.5           # soglia interesse istituzionale
RVOL_BREAKOUT = 2.0           # soglia Setup B
# RVOL nello screener: default = punteggio combinato 0.7*RS + 0.3*RVOL cappato
# (ordina i candidati, non li taglia). True = scarta i candidati con
# RVOL < RVOL_INTEREST. Confrontare le due varianti con engine/backtest.py.
RVOL_HARD_FILTER = False
MAX_STOP_ATR = 2.5            # geometria sfavorevole oltre questa distanza
WATCHLIST_SIZE = 10
VIX_HALT = 30.0
FUNDING_EXTREME = 0.0005      # 0.05% per 8h
# Funding oltre FUNDING_EXTREME contro la direzione del trade: True = il row
# diventa status "blocked" (non operabile), False = solo warning testuale.
FUNDING_BLOCK = True

# --- Default impostazioni utente ---
DEFAULT_SETTINGS = {
    "capital": 4000.0,
    "risk_pct": 1.0,
    "telegram_token": "",
    "telegram_chat_id": "",
    "scan_interval_min": 30,
}
