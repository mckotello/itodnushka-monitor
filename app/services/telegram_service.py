import httpx

from app.core.config import settings


async def send_telegram_message(message: str) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False

    url = (
        f"https://api.telegram.org/bot"
        f"{settings.telegram_bot_token}/sendMessage"
    )

    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": message,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)

        response.raise_for_status()
        return True

    except httpx.HTTPError:
        return False