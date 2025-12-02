import httpx

from app.core.config import settings
from app.core.logging_config import logger
from app.services.signature_service import generate_signature

class AckService:
    @staticmethod
    async def send_ack(url: str, payload: dict, ack_type: str = "CMS") -> httpx.Response:
        signature = generate_signature(payload)
        headers = {"X-DF-Signature": signature, "Content-Type": "application/json"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            logger.info(f"ACK sent to {url} for {ack_type}. Status: {response.status_code}")
            return response
        except httpx.RequestError as exc:
            logger.error(f"Network error while sending ACK to {url} for {ack_type}: {exc}")
            raise
