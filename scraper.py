import pandas as pd
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; CryptoDailyMailer/1.0; +https://github.com/)",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_html(url: str, timeout=20) -> str:
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    r = s.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def parse_table(html: str) -> pd.DataFrame:
    dfs = pd.read_html(html)
    df = next((d for d in dfs if "Ticker" in d.columns), None)
    if df is None:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")
        df = pd.read_html(str(table))[0]

    def to_num(x):
        if pd.isna(x): return x
        s = str(x).replace("%","").replace(",","").strip()
        try: return float(s)
        except: return pd.NA

    for c in df.columns:
        if "Perf" in c or c in ["Price"]:
            df[c] = df[c].apply(to_num)
    if "Ticker" in df.columns:
        df["Ticker"] = df["Ticker"].astype(str).str.upper()
    return df

def get_crypto_table(url: str) -> pd.DataFrame:
    html = fetch_html(url)
    return parse_table(html)
