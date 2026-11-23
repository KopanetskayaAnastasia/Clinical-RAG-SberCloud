import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.retrieval import search_chunks

query = "Как система использует медицинские документы для формирования ответа?"

print("=== ТЕСТ СЕМАНТИЧЕСКОГО ПОИСКА ===")
print("Запрос:", query)

results = search_chunks(query, top_k=3)

print("\n=== РЕЗУЛЬТАТЫ ПОИСКА ===")
print("Найдено фрагментов:", len(results))

for index, item in enumerate(results, start=1):
    print(f"\nФрагмент №{index}")
    print("Текст:", item["chunk_text"])
    print("Косинусное расстояние:", round(item["distance"], 6))
    print("Количество токенов:", item["token_count"])

if results:
    print("\nУСПЕХ: семантический поиск работает")
else:
    print("\nВ базе пока нет подходящих фрагментов")
