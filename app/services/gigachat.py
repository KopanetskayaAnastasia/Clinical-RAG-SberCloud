import os
import uuid
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://api.giga.chat/v1/chat/completions"

CA_BUNDLE = str(
    Path(__file__).resolve().parents[2]
    / "certs"
    / "combined-ca.pem"
)


def get_access_token():
    auth_key = os.getenv("GIGACHAT_AUTH_KEY")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

    if not auth_key:
        raise ValueError("Не задан GIGACHAT_AUTH_KEY")

    if not Path(CA_BUNDLE).exists():
        raise FileNotFoundError(f"Файл сертификатов не найден: {CA_BUNDLE}")

    response = httpx.post(
        AUTH_URL,
        headers={
            "Authorization": f"Basic {auth_key}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"scope": scope},
        timeout=30,
        verify=CA_BUNDLE
    )

    response.raise_for_status()
    return response.json()["access_token"]


def generate_answer(question: str, context: str) -> str:
    if not question.strip():
        raise ValueError("Вопрос не должен быть пустым")

    if not context.strip():
        return "Недостаточно данных в найденных документах для ответа."

    token = get_access_token()
    model = os.getenv("GIGACHAT_MODEL", "GigaChat-3-Pro")

    response = httpx.post(
        CHAT_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Ты ассистент для работы с медицинскими клиническими "
                        "рекомендациями. Отвечай только на основании переданного "
                        "контекста. Не добавляй сведения из собственных знаний. "
                        "Если контекста недостаточно, прямо сообщи об этом. "
                        "Не придумывай медицинские рекомендации и источники. "
                        "Указывай название документа, если оно присутствует "
                        "в контексте."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Вопрос пользователя:\n{question}\n\n"
                        f"Контекст из документов:\n{context}\n\n"
                        "Сформируй ответ на основании контекста."
                    )
                }
            ],
            "temperature": 0.1
        },
        timeout=90,
        verify=CA_BUNDLE
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

