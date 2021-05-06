import json
import os
import urllib.parse
import urllib.request

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_CHAT_ID = os.environ.get("TELEGRAM_BOT_CHAT_ID")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN:
        return

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {
        "chat_id": TELEGRAM_BOT_CHAT_ID,
        "parse_mode": "Markdown",
        "text": message,
    }

    request_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    request = urllib.request.Request(
        request_url, data=json.dumps(data).encode(), headers=headers
    )
    response = urllib.request.urlopen(request)
    return response.read().decode("utf-8")


def send_slack_message(message):
    if not SLACK_WEBHOOK_URL:
        return

    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "text": message,
    }

    request_url = SLACK_WEBHOOK_URL
    request = urllib.request.Request(
        request_url, data=json.dumps(data).encode(), headers=headers
    )
    response = urllib.request.urlopen(request)
    return response.read().decode("utf-8")


def send_alerts(message):
    send_telegram_message(message)
    send_slack_message(message)
