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

def push(message: str):
    """ Send a push notification over PUSHOVER"""
    print(f"Push: {message}")
    payload = {"user": PUSHOVER_TOKEN, "token": PUSHOVER_TOKEN, "message":message}
    requests.load(PUSHOVER_URL, data=payload)

def send_message(subject: str, text_body: str, html_body: str):
    """Send via email, push or console - whichever is available"""
    if USE_EMAIL:
        send_email(subject, text_body, html_body)
        print(f"Email sent with the subject {text_body}")
    elif USE_PUSH:
        push(f"Subject: {subject}\n\n{text_body}")
    else:
        print(f"\n{'='*50}")
        print(f"📧 EMAIL OUTPUT (console fallback)")
        print(f"{'='*50}")
        print(f"Subject: {subject}\n")
        print(text_body)
        print(f"{'='*50}\n")
    
@function_tool
def send_email_tool(subject: str, text_body: str, html_body: str):
    """ 
    Send out an email with the given subject and body to all sales prospects.
    Args:
        subject: The subject of the email
        text_body: The body of the email as plain text
        html_body: The HTML body of the email
    """

    send_message(subject, text_body, html_body)

COMPANY_INTRO = """
You are a sales agent working for ComplAI,
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
You write emails.
"""

sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=COMPANY_INTRO + "Your email style is professional, serious, with gravitas and credibility.",
    model=MODEL_NAME,
)

sales_agent2 = Agent(
    name="Humorous Sales Agent",
    instructions=COMPANY_INTRO + "Your email style is witty, engaging, and humorous.",
    model=MODEL_NAME,
)

sales_agent3 = Agent(
    name="Executive Sales Agent",
    instructions=COMPANY_INTRO + "Your email style is concise, to the point, in the style of a busy senior executive.",
    model=MODEL_NAME,
)

sales_picker = Agent(
    name="Excecutive Sales Agent",
    instructions="""
    you pick the best cold email from the given options,
    Imagine you are the customer and pick one you are most likely to respond to.
    Do not give explanations; reply only with the selected email only.
    """,
    model=MODEL_NAME
)

sales_refiner = Agent(
    name="Sales Refiner",
    instructions="""
You are an expert email editor. You receive a draft sales email and improve it:
- Tighten the language and remove filler words
- Strengthen the call-to-action so the reader is compelled to reply
- Improve the subject line to boost open rates
- Keep the same overall tone and voice of the original

Reply with the refined email only. Start with "Subject: ..." on the first line, followed by a blank line, then the email body.
""",
    model=MODEL_NAME
)

async def main():
    print("=" * 55)
    print("  📧  SDR EMAIL AGENT — Exercise Project")
    print("=" * 55)

    # Show setup status
    if USE_EMAIL:
        print("  ✅ Email (SMTP) is configured")
    elif USE_PUSH:
        print("  ✅ Pushover is configured (email fallback)")
    else:
        print("  ⚠️  No email/push configured — output to console only")

    print()
    print("  Choose an orchestration method:")
    print("    1) Orchestrating by Code")
    print("    2) Orchestrating by LLMs (via Tools)")
    print()

    choice  = input(" Enter 1 or 2 ").strip()

    if choice == "1":
        from method1_code import run_method1
        await run_method1()
    elif choice == "2":
        from method2_tools import run_method2
        await run_method2()
    else:
        print("Invalid choice. Please run again and enter 1 or 2.")

if __name__ == "__main__":
    asyncio.run(main())
