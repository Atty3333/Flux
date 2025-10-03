from win10toast import ToastNotifier
from datetime import datetime, time, timedelta
import pytz
from email.mime.text import MIMEText
import smtplib
import requests
import os

def notify(title,message):
    BOT_TOKEN = "7872379298:AAGnZQhgOl2SFums-b-2014CVfiVj3nxTCo"
    CHAT_ID = "7938170303"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": title+" "+message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def send_email_error(subject, error_message):
    sender_email = "Mutemaletso@gmail.com"
    receiver_email = "Mutemaletso@gmail.com"
    app_password = "lscq ihxb wfmr mzyt"

    msg = MIMEText(error_message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ Error email sent.")
    except Exception as e:
        print("❌ Failed to send error email:", str(e))

def schedule():
    # Botswana time zone
    local_tz = pytz.timezone("Africa/Gaborone")

    # Current local time
    now_local = datetime.now(local_tz)

    # Build target time today at 8 PM
    target_naive = datetime(now_local.year, now_local.month, now_local.day, 20, 0, 0)
    target_local = local_tz.localize(target_naive)

    # If it's already past 7:45 PM local time, move to tomorrow
    if target_local < now_local + timedelta(minutes=15):
        target_local += timedelta(days=1)

    # Convert to UTC
    publish_time_utc = target_local.astimezone(pytz.utc)
    print(publish_time_utc)
    # Return datetime object in UTC
    return publish_time_utc


def log_error_to_file(error_message):
    LOG_FILE = "error_log.txt"
    """Log the error with date/time to a file."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")

def get_path(*path_parts):
    """
    Resolves a path relative to the project root (one folder above main file).
    Example: get_path("clips", "source_video.mp4")
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, *path_parts)