# agents/apply.py
# ─────────────────────────────────────────────────────────
#  Email Application Sender
#  Uses Gmail SMTP — completely free
# ─────────────────────────────────────────────────────────

import os
import time
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from config import USER_PROFILE, DELAY_BETWEEN_APPLIES_SEC

log = logging.getLogger("apply")

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# Daily send counter
_daily = {"date": "", "count": 0}

def _today_count() -> int:
    from datetime import date
    today = str(date.today())
    if _daily["date"] != today:
        _daily["date"]  = today
        _daily["count"] = 0
    return _daily["count"]

def _increment():
    _daily["count"] += 1


def send_application(job: dict, cover_letter: str,
                     max_per_day: int = 10) -> dict:
    """
    Send one email application with your CV attached.

    Returns:
        { sent: bool, error: str|None }
    """
    if not job.get("apply_email"):
        return {"sent": False, "error": "No apply email found for this job."}

    if _today_count() >= max_per_day:
        return {"sent": False,
                "error": f"Daily limit of {max_per_day} reached. Try again tomorrow."}

    gmail_addr   = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "")

    if not gmail_addr or not app_password or app_password == "xxxxxxxxxxxxxxxx":
        return {"sent": False,
                "error": "GMAIL_ADDRESS or GMAIL_APP_PASSWORD missing in .env"}

    # Build email
    msg             = MIMEMultipart()
    msg["From"]     = f"{USER_PROFILE['name']} <{gmail_addr}>"
    msg["To"]       = job["apply_email"]
    msg["Subject"]  = (
        f"Job Application – {job.get('title', 'Position')} "
        f"– {USER_PROFILE['name']}"
    )
    msg.attach(MIMEText(cover_letter, "plain"))

    # Attach CV
    cv_path = Path(os.getenv("CV_PATH", "./assets/Jasper_John_Paitan_CV.pdf"))
    if cv_path.exists():
        with open(cv_path, "rb") as f:
            att = MIMEApplication(f.read(), _subtype="pdf")
            att.add_header("Content-Disposition", "attachment",
                           filename=cv_path.name)
            msg.attach(att)
    else:
        log.warning(f"CV not found at {cv_path} — sending without attachment")

    # Send
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_addr, app_password)
            server.send_message(msg)

        _increment()
        log.info(f"  ✅ Sent → {job['apply_email']} | {job['title']}")
        time.sleep(DELAY_BETWEEN_APPLIES_SEC)
        return {"sent": True, "error": None}

    except smtplib.SMTPAuthenticationError:
        return {"sent": False,
                "error": (
                    "Gmail auth failed.\n"
                    "Fix: re-generate your App Password at "
                    "myaccount.google.com/apppasswords"
                )}
    except smtplib.SMTPRecipientsRefused:
        return {"sent": False,
                "error": f"Email refused: {job['apply_email']}"}
    except Exception as e:
        return {"sent": False, "error": str(e)}
