import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(smtp_cfg: dict, subject: str, html_body: str, text_body: str):
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
