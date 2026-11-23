import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv(
    "CLOUDRU_EMBEDDING_MODEL",
    "ai-sage/Giga-Embeddings-instruct-3B"
)

EXPECTED_DIMENSION = 2048


def get_embeddings_client():
    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError("Не найден API_KEY в файле .env")

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv(
            "CLOUDRU_BASE_URL",
            "https://foundation-models.api.cloud.ru/v1"
        )
    )


def create_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Текст для векторизации пуст")

    client = get_embeddings_client()

    try:
        response = client.embeddings.create(
            model=MODEL,
            input=text
        )

        vector = response.data[0].embedding

        if len(vector) != EXPECTED_DIMENSION:
            raise ValueError(
                f"Ожидалось {EXPECTED_DIMENSION} измерений, "
                f"получено {len(vector)}"
            )

        return vector

    finally:
        client.close()


def create_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    client = get_embeddings_client()

    try:
        response = client.embeddings.create(
            model=MODEL,
            input=texts
        )

        vectors = [item.embedding for item in response.data]

        if len(vectors) != len(texts):
            raise ValueError("Количество эмбеддингов не совпадает с количеством текстов")

        for vector in vectors:
            if len(vector) != EXPECTED_DIMENSION:
                raise ValueError(
                    f"Некорректная размерность эмбеддинга: {len(vector)}"
                )

        return vectors

    finally:
        client.close()
