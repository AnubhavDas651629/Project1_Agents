import asyncio
import os
import smtplib
from email.message import EmailMessage

import requests
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool, ModelSettings

load_dotenv(override=True)

MODEL_NAME = "openai/gpt-oss-120b"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
USE_EMAIL = bool(EMAIL_ADDRESS and EMAIL_SMTP_SERVER and EMAIL_APP_PASSWORD)

PUSHOVER_USER = os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"
USE_PUSH = bool(PUSHOVER_USER and PUSHOVER_TOKEN)

def send_email(subject: str, text_body: str, html_body: str):
    """Send an email via SMTP"""
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype= "html")
    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)



