import httpx
import smtplib
from email.message import EmailMessage
import json
import logging

logger = logging.getLogger(__name__)

async def execute_webhook(url: str, method: str, headers: dict, payload: dict):
    async with httpx.AsyncClient() as client:
        req_method = getattr(client, method.lower(), client.post)
        response = await req_method(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json() if response.text else {}

async def send_slack_message(webhook_url: str, message: str):
    async with httpx.AsyncClient() as client:
        payload = {"text": message}
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()
        return {"status": "sent"}

def send_email_smtp(smtp_host: str, smtp_port: int, username: str, password: str, to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
    return {"status": "sent"}

async def sync_crm_dummy(api_key: str, contact_data: dict):
    # Mocking CRM sync (e.g. HubSpot)
    logger.info(f"Mocking CRM sync with API key: {api_key[:4]}... Data: {contact_data}")
    return {"status": "synced", "contact_id": "dummy_12345"}

async def sync_crm_hubspot(api_key: str, contact_data: dict):
    if not api_key:
        raise ValueError("Missing HubSpot API key")
    payload = {
        "properties": {
            "email": contact_data.get("email"),
            "firstname": contact_data.get("first_name") or contact_data.get("name"),
            "lastname": contact_data.get("last_name"),
            "phone": contact_data.get("phone"),
            "company": contact_data.get("company"),
        }
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            headers=headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()
