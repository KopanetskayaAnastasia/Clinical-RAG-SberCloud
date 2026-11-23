import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.parser import parse_document
from app.services.chunker import chunk_document

file_path = PROJECT_ROOT / "documents" / "sample_guidelines" / "test_guideline.txt"

print("[1] Извлечение текста")
pages = parse_document(str(file_path))

print("[2] Разбиение на фрагменты")
chunks = chunk_document(pages)

print("Количество фрагментов:", len(chunks))

for chunk in chunks:
    print("\nФрагмент:", chunk["chunk_index"])
    print("Токенов:", chunk["token_count"])
    print("Страница:", chunk["page_number"])
    print("Текст:", chunk["chunk_text"])

print("\nУСПЕХ: разбиение на фрагменты работает")
