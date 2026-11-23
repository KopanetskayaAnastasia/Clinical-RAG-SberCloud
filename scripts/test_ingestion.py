import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.ingestion import ingest_document
from app.services.clickhouse import get_clickhouse_client

file_path = (
    PROJECT_ROOT
    / "documents"
    / "sample_guidelines"
    / "test_guideline.txt"
)

print("=== ТЕСТ ЗАГРУЗКИ ДОКУМЕНТА ===")

result = ingest_document(str(file_path))

print("\n=== РЕЗУЛЬТАТ ===")
for key, value in result.items():
    print(f"{key}: {value}")

client = get_clickhouse_client()

try:
    documents = client.query(
        "SELECT count() FROM documents"
    ).result_rows[0][0]

    chunks = client.query(
        "SELECT count() FROM document_chunks"
    ).result_rows[0][0]

    print("\n=== ПРОВЕРКА CLICKHOUSE ===")
    print("Документов в базе:", documents)
    print("Фрагментов в базе:", chunks)

finally:
    client.close()

print("\nУСПЕХ: документ загружен в ClickHouse")
