import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.rag import ask_rag

question = "Что содержат клинические рекомендации и как RAG-система использует их?"

print("=== ПОЛНЫЙ ТЕСТ RAG-СИСТЕМЫ ===")
print("Вопрос:", question)

result = ask_rag(question, top_k=3)

print("\n=== ОТВЕТ СИСТЕМЫ ===")
print(result["answer"])

print("\n=== ИСТОЧНИКИ ===")
for index, source in enumerate(result["sources"], start=1):
    print(f"\nИсточник {index}")
    print("Document ID:", source["document_id"])
    print("Chunk ID:", source["chunk_id"])
    print("Текст:", source["text"])
    print("Косинусное расстояние:", round(source["distance"], 6))

print("\n=== МЕТРИКИ ===")
print("Найдено фрагментов:", result["retrieved_chunks"])
print("Недостаточно данных:", result["insufficient_data"])
print("Время выполнения, мс:", result["response_time_ms"])

if result["retrieved_chunks"] > 0 and result["answer"].strip():
    print("\nУСПЕХ: полный RAG-контур работает")
else:
    print("\nПРОВЕРКА НЕ ПРОЙДЕНА")
