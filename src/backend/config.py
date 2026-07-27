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

# --- Parametri setup per mercato (Fase 5) ---
# ATTENZIONE: questi valori sono IPOTESI INIZIALI, non parametri validati.
# Vanno confermati o smentiti con engine/backtest.py (confronto
# --params default vs --params market) prima di considerarli definitivi.
MARKET_PARAMS = {
    "crypto": {
        "RANGE_BARS": 21,          # crypto quota 24/7: ~3 settimane = 21 barre
        "SQUEEZE_LOOKBACK": 84,    # ~12 settimane di calendario
        "RSI_LONG_MIN": 35,        # pullback crypto più profondi: soglia più permissiva
        "RSI_SHORT_MAX": 65,
    },
    "stocks": {
        "RANGE_BARS": 15,          # ~3 settimane di borsa
        "SQUEEZE_LOOKBACK": 60,    # ~12 settimane di borsa
        "RSI_LONG_MIN": 40,
        "RSI_SHORT_MAX": 60,
    },
}

# --- Parametri multi-timeframe (FASE 3) ---
# IPOTESI NON VALIDATE: usati solo per disegnare livelli / timing informativo.
# Perché i moltiplicatori d'invalidazione crescono scendendo di TF: sui TF bassi
# il rapporto rumore/ATR cresce e i costi incidono di più sul rischio unitario.
TF_PARAMS = {
    "D": {
        "RANGE_BARS": 15,
        "SQUEEZE_LOOKBACK": 60,
        "INVALIDATION_ATR": 1.5,
        "MIN_BARS": 220,
        "BINANCE_INTERVAL": "1d",
    },
    "4H": {
        "RANGE_BARS": 30,
        "SQUEEZE_LOOKBACK": 90,
        "INVALIDATION_ATR": 1.75,
        "MIN_BARS": 120,
        "BINANCE_INTERVAL": "4h",
    },
    "1H": {
        "RANGE_BARS": 40,
        "SQUEEZE_LOOKBACK": 120,
        "INVALIDATION_ATR": 2.0,
        "MIN_BARS": 160,
        "BINANCE_INTERVAL": "1h",
    },
    "15m": {
        "RANGE_BARS": 48,
        "SQUEEZE_LOOKBACK": 144,
        "INVALIDATION_ATR": 2.5,
        "MIN_BARS": 200,
        "BINANCE_INTERVAL": "15m",
    },
}
# Watchlist entry: solo questi TF. 1H/15m = timing su asset già in watchlist.
WATCHLIST_ENTRY_TFS = ("D", "4H")
TIMING_TFS = ("1H", "15m")
TIMING_ALERT_COOLDOWN_S = 4 * 3600  # max 1 notifica timing per asset / 4h

# --- Playbook thresholds (FASE 4 / 5-BIS) ---
# IPOTESI NON VALIDATE, da calibrare su casi reali.
# Stati qualitativi ↑/↓/→ consumati da display e (poi) matching playbook.
PLAYBOOK_THRESHOLDS = {
    "oi": {
        "up_pct_24h": 0.05,          # +5% su 24h → "up"
        "down_pct_24h": -0.05,       # −5% su 24h → "down"
        "collapse_pct_24h": -0.20,   # −20% su 24h → "collapse"
    },
    "cvd": {
        "slope_bars": 20,            # regressione lineare su N barre
        # Calibrato 2026-07-27 su scan live (BTC/ETH/ZEC/TRX): |slope| tipica
        # 0.01–0.04 con soglia ±0.1 → tutto flat. Portata a ±0.02 (down_strong
        # −0.06 in proporzione) per separare pressione lieve dal rumore.
        # IPOTESI NON VALIDATE — da riaffinare sull'uso reale, non in questa fase.
        "up": 0.02,
        "down": -0.02,
        "down_strong": -0.06,
    },
    "prezzo": {
        # Stessa banda usata da classify_price (FASE 4): un solo punto di verità.
        "flat_band": 0.005,          # |Δ| < 0.5% → flat (TF rif. 4H, lookback 6)
        "lookback_bars": 6,
    },
    "rvol": {
        "high": 1.5,
        "low": 1.0,
    },
}

# Cache disco OI hist (period 4h): TTL 1h — coerente col TF, evita hammering REST.
OI_HIST_CACHE_TTL_S = 3600
OI_HIST_PERIOD = "4h"
FUTURES_KLINES_CACHE_TTL_S = 900  # 15m — CVD da klines futures chiuse

# FASE 5 — pesi non validati, sola funzione di ordinamento dell'attenzione.
# Somma = 1.0. Componenti mancanti (es. OI/CVD su stock) escluse + rinormalizzazione.
CONFLUENCE_WEIGHTS = {
    "tech": 0.15,        # situazione tecnica D/4H presente
    "rs": 0.20,          # rank forza relativa
    "cvd_long": 0.25,    # coerenza CVD col lato long (maggior peso informativo)
    "oi_expand": 0.20,   # OI in espansione / non collasso
    "funding_ok": 0.10,  # funding non contrario estremo
    "rvol": 0.10,        # RVOL in salita / interesse
}

# FASE 5-BIS: includi scenario prioritario negli alert watchlist (mai schede protezione).
PLAYBOOK_IN_ALERTS = True

# --- Default impostazioni utente ---
DEFAULT_SETTINGS = {
    "capital": 4000.0,
    "risk_pct": 1.0,
    "telegram_token": "",
    "telegram_chat_id": "",
    "scan_interval_min": 30,
}
