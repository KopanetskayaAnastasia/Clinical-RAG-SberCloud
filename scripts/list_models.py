import os
import uuid
import httpx
from dotenv import load_dotenv

load_dotenv()

with httpx.Client(
    timeout=40,
    verify="certs/combined-ca.pem"
) as client:

    response = client.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers={
            "Authorization": f"Basic {os.getenv('GIGACHAT_AUTH_KEY')}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "scope": os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        }
    )
    response.raise_for_status()
    token = response.json()["access_token"]

    response = client.get(
        "https://api.giga.chat/v1/models",
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()

    print("ДОСТУПНЫЕ МОДЕЛИ:")

    for model in response.json().get("data", []):
        print("-", model.get("id"))