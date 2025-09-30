import os, json

def getenv(name, default=None, required=False):
    v = os.getenv(name, default)
    if required and (v is None or v == ""):
        raise RuntimeError(f"Missing required env var: {name}")
    return v

def load_tickers():
    raw = os.getenv("TICKERS", "").strip()
    if raw:
        return [t.strip().upper() for t in raw.split(",") if t.strip()]
    if os.path.exists("tickers.json"):
        with open("tickers.json", "r", encoding="utf-8") as f:
            j = json.load(f)
            return [t.strip().upper() for t in j.get("tickers", [])]
    return []

CFG = {
    "URL": "https://finviz.com/crypto_performance.ashx?p=d",
    "TZ": os.getenv("TZ", "Europe/Paris"),
    "SMTP": {
        "HOST": getenv("SMTP_HOST", required=True),
        "PORT": int(getenv("SMTP_PORT", "587")),
        "USER": getenv("SMTP_USER", required=True),
        "PASS": getenv("SMTP_PASS", required=True),
        "FROM": getenv("MAIL_FROM", required=True),
        "TO": [x.strip() for x in getenv("MAIL_TO", required=True).split(",")],
    },
    "TICKERS": load_tickers(),
    "API_KEY": os.getenv("API_KEY", ""),  # clé pour protéger /send
}
