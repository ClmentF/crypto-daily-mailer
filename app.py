from fastapi import FastAPI, Query, HTTPException, Header, Response
from typing import List, Optional
import pandas as pd
from config import CFG
from scraper import get_crypto_table
from render import render_html, render_text
from emailer import send_email

app = FastAPI(title="Crypto Daily API", version="1.0.0")

def filter_tickers(df: pd.DataFrame, tickers: List[str]) -> pd.DataFrame:
    if not tickers or "Ticker" not in df.columns:
        return df
    return df[df["Ticker"].isin([t.upper() for t in tickers])].reset_index(drop=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/report")
def report(tickers: Optional[str] = Query(None), fmt: str = Query("json")):
    """fmt=json|html  ; tickers='BTCUSD,ETHUSD' (optionnel)"""
    df = get_crypto_table(CFG["URL"])
    if df is None or df.empty:
        raise HTTPException(502, "Source indisponible")
    sel = [t.strip().upper() for t in tickers.split(",")] if tickers else CFG["TICKERS"]
    df = filter_tickers(df, sel)

    if fmt == "json":
        return {"count": len(df), "rows": df.to_dict(orient="records")}
    elif fmt == "html":
        html = render_html(df, CFG["TZ"])
        return Response(content=html, media_type="text/html")
    else:
        raise HTTPException(400, "fmt doit être json ou html")

@app.post("/send")
def send(
    tickers: Optional[str] = Query(None),
    x_api_key: str = Header(None)  # petite protection simple
):
    expected = CFG.get("API_KEY") or ""
    if expected and x_api_key != expected:
        raise HTTPException(401, "Unauthorized")

    df = get_crypto_table(CFG["URL"])
    if df is None or df.empty:
        raise HTTPException(502, "Source indisponible")

    sel = [t.strip().upper() for t in tickers.split(",")] if tickers else CFG["TICKERS"]
    df = filter_tickers(df, sel)
    if df.empty:
        raise HTTPException(400, "Aucun ticker après filtrage")

    html = render_html(df, CFG["TZ"])
    text = render_text(df, CFG["TZ"])
    send_email(CFG["SMTP"], f"[Crypto Daily] {len(df)} tickers", html, text)
    return {"status": "sent", "tickers": sel or "ALL"}
