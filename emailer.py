import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests

def _send_via_smtp(smtp_cfg: dict, subject: str, html_body: str, text_body: str):
    msg = MIMEMultipart("alternative")
    msg["From"] = smtp_cfg["FROM"]
    msg["To"] = ", ".join(smtp_cfg["TO"])
    msg["Subject"] = subject
    msg.attach(MIMEText(text_body, "plain", _charset="utf-8"))
    msg.attach(MIMEText(html_body, "html", _charset="utf-8"))
    with smtplib.SMTP(smtp_cfg["HOST"], smtp_cfg["PORT"]) as server:
        server.starttls()
        server.login(smtp_cfg["USER"], smtp_cfg["PASS"])
        server.sendmail(smtp_cfg["FROM"], smtp_cfg["TO"], msg.as_string())

def _send_via_sendgrid(smtp_cfg: dict, subject: str, html_body: str, text_body: str):
    api_key = os.getenv("SENDGRID_API_KEY", "")
    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY manquant")
    data = {
        "personalizations": [{"to": [{"email": to} for to in smtp_cfg["TO"]]}],
        "from": {"email": smtp_cfg["FROM"]},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": text_body},
            {"type": "text/html", "value": html_body},
        ],
    }
    r = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=data,
        timeout=30,
    )
    if r.status_code >= 300:
        raise RuntimeError(f"SendGrid error {r.status_code}: {r.text}")

def send_email(smtp_cfg: dict, subject: str, html_body: str, text_body: str):
    if os.getenv("USE_SENDGRID", "0") == "1":
        _send_via_sendgrid(smtp_cfg, subject, html_body, text_body)
    else:
        _send_via_smtp(smtp_cfg, subject, html_body, text_body)
