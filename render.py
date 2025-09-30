from datetime import datetime
import pytz
import pandas as pd

def _fmt_pct(x):
    if pd.isna(x): return ""
    sign = "+" if x > 0 else ""
    return f"{sign}{x:.2f}%"

def render_summary(df: pd.DataFrame):
    if "Perf Day" not in df.columns or df.empty:
        return "Aucun résumé disponible."
    top = df.sort_values("Perf Day", ascending=False).iloc[0]
    flop = df.sort_values("Perf Day", ascending=True).iloc[0]
    return f"Top: {top['Ticker']} ({_fmt_pct(top['Perf Day'])}) — Flop: {flop['Ticker']} ({_fmt_pct(flop['Perf Day'])})"

def render_html(df: pd.DataFrame, tz: str) -> str:
    now = datetime.now(pytz.timezone(tz))
    title = f"État des cryptos — {now.strftime('%d/%m/%Y %H:%M %Z')}"
    cols = [c for c in ["Ticker","Price","Perf Day","Perf Week","Perf Month","Perf YTD","Perf Year"] if c in df.columns]
    dff = df[cols].copy()
    for c in cols:
        if "Perf" in c:
            dff[c] = dff[c].apply(_fmt_pct)
        elif c == "Price":
            dff[c] = dff[c].apply(lambda v: f"{v:.4f}" if pd.notna(v) else "")
    table_html = dff.to_html(index=False, escape=False)
    summary = render_summary(df)
    style = """
      <style>
        body { font-family: Arial, sans-serif; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background: #f2f2f2; text-align: left; }
      </style>
    """
    return f"""<html><head>{style}</head><body>
      <h2>{title}</h2>
      <p>{summary}</p>
      {table_html}
      <p style="margin-top:16px;color:#666">Source: Finviz (1 requête/jour, usage pédagogique).</p>
    </body></html>"""

def render_text(df: pd.DataFrame, tz: str) -> str:
    now = datetime.now(pytz.timezone(tz))
    lines = [f"Etat des cryptos — {now.strftime('%d/%m/%Y %H:%M %Z')}"]
    if "Ticker" in df.columns:
        for _, r in df.head(20).iterrows():
            part = [str(r["Ticker"])]
            if "Price" in df.columns and pd.notna(r["Price"]):
                part.append(f"Price={r['Price']:.4f}")
            if "Perf Day" in df.columns and pd.notna(r["Perf Day"]):
                part.append(f"Day={r['Perf Day']:.2f}%")
            lines.append(" | ".join(part))
    return "\n".join(lines)
