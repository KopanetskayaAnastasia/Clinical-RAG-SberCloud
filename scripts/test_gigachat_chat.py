import os
import uuid
import httpx
from dotenv import load_dotenv

load_dotenv()

with httpx.Client(
    timeout=60,
    verify="certs/combined-ca.pem"
) as client:

    print("[1] Получение токена")

    auth = client.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers={
            "Authorization": f"Basic {os.getenv('GIGACHAT_AUTH_KEY')}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"scope": os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")}
    )
    auth.raise_for_status()
    token = auth.json()["access_token"]
    print("Токен получен")

    print("\n[2] Запрос к модели")

    response = client.post(
        "https://api.giga.chat/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "model": os.getenv("GIGACHAT_MODEL", "GigaChat"),
            "messages": [
                {
                    "role": "user",
                    "content": "Ответь одной фразой: GigaChat успешно подключён к медицинскому RAG-проекту."
                }
            ],
            "temperature": 0.1
        }
    )

    print("HTTP:", response.status_code)
    print("Ответ сервера:", response.text[:2000])
    response.raise_for_status()

    answer = response.json()["choices"][0]["message"]["content"]

    print("ГЕНЕРАЦИЯ УСПЕШНА")
    print("Ответ модели:", answer)