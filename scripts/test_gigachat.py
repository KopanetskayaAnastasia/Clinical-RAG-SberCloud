import os
import uuid
import httpx
from dotenv import load_dotenv

load_dotenv()

auth_key = os.getenv("GIGACHAT_AUTH_KEY")
scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

if not auth_key:
    print("Ключ не найден")
    raise SystemExit(1)

try:
    with httpx.Client(
        timeout=40,
        verify="certs/combined-ca.pem"
    ) as client:

        print("[1] Получаем токен...")

        response = client.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                "Authorization": f"Basic {auth_key}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            },
            data={"scope": scope}
        )
        response.raise_for_status()
        token = response.json()["access_token"]

        print("Токен получен")

        addresses = [
            "https://api.giga.chat/v1/models",
            "https://gigachat.devices.sberbank.ru/api/v1/models"
        ]

        for address in addresses:
            print("\nПроверяем:", address)

            try:
                result = client.get(
                    address,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    }
                )

                print("HTTP:", result.status_code)

                if result.is_success:
                    print("ПОДКЛЮЧЕНИЕ УСПЕШНО")
                    print("Ответ получен от GigaChat")
                else:
                    print("Ответ сервера:", result.text[:500])

            except httpx.HTTPError as error:
                print("Ошибка соединения:", type(error).__name__)
                print(str(error)[:300])

except httpx.HTTPError as error:
    print("Ошибка получения токена:", type(error).__name__)
    print(str(error)[:500])