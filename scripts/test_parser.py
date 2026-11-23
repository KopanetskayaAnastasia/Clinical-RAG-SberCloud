import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.parser import parse_document

file_path = PROJECT_ROOT / "documents" / "sample_guidelines" / "test_guideline.txt"

print("[1] Проверка извлечения текста")

pages = parse_document(str(file_path))

print("Количество текстовых блоков:", len(pages))
print("Номер страницы:", pages[0]["page_number"])
print("Извлечённый текст:")
print(pages[0]["text"])

print("\nУСПЕХ: парсер документов работает")
