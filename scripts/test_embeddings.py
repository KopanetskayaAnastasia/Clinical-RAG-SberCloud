import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("API_KEY")
base_url = os.getenv(
    "CLOUDRU_BASE_URL",
    "https://foundation-models.api.cloud.ru/v1"
)
model = os.getenv(
    "CLOUDRU_EMBEDDING_MODEL",
    "ai-sage/Giga-Embeddings-instruct-3B"
)

if not api_key:
    raise ValueError("Не найден API_KEY в файле .env")

print("[1] Подключение к Cloud.ru Foundation Models")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

print("[2] Отправка медицинского текста на векторизацию")

response = client.embeddings.create(
    model=model,
    input=[
        "Клинические рекомендации Минздрава РФ "
        "по диагностике и лечению артериальной гипертензии."
    ]
)

vector = response.data[0].embedding

print("\nУСПЕХ: эмбеддинг получен")
print("Модель:", model)
print("Размерность вектора:", len(vector))
print("Количество обработанных токенов:", response.usage.prompt_tokens)
print("Первые 5 значений:", vector[:5])