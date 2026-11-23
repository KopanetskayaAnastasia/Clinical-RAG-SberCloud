from pathlib import Path
from uuid import uuid4

from app.services.parser import parse_document
from app.services.chunker import chunk_document
from app.services.embeddings import create_embeddings
from app.services.clickhouse import get_clickhouse_client


def ingest_document(
    file_path: str,
    filename: str | None = None,
    storage_info=None
) -> dict:
    path = Path(file_path)
    document_filename = filename or path.name

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    print("[1] Извлечение текста")
    pages = parse_document(str(path))

    print("[2] Разбиение на фрагменты")
    chunks = chunk_document(pages)

    if not chunks:
        raise ValueError("Документ не содержит текстовых фрагментов")

    print("[3] Получение эмбеддингов")
    texts = [chunk["chunk_text"] for chunk in chunks]
    embeddings = create_embeddings(texts)

    if len(embeddings) != len(chunks):
        raise ValueError(
            "Количество эмбеддингов не совпадает с количеством чанков"
        )

    if not embeddings or not embeddings[0]:
        raise ValueError("Не удалось получить эмбеддинги документа")

    document_id = uuid4()

    print("[4] Запись в ClickHouse")

    client = get_clickhouse_client()

    try:
        client.insert(
            "documents",
            [[
                document_id,
                document_filename,
                Path(document_filename).stem,
                document_filename,
                "clinical_guideline",
                None,
                "",
                len(chunks),
                "processed"
            ]],
            column_names=[
                "document_id",
                "filename",
                "title",
                "source",
                "document_type",
                "publication_date",
                "version",
                "total_chunks",
                "status"
            ]
        )

        chunk_rows = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_rows.append([
                document_id,
                chunk["chunk_index"],
                chunk["chunk_text"],
                chunk["page_number"],
                chunk["token_count"],
                embedding
            ])

        client.insert(
            "document_chunks",
            chunk_rows,
            column_names=[
                "document_id",
                "chunk_index",
                "chunk_text",
                "page_number",
                "token_count",
                "embedding"
            ]
        )

        result = {
            "document_id": str(document_id),
            "filename": document_filename,
            "chunks_count": len(chunks),
            "embedding_dimension": len(embeddings[0]),
            "status": "processed"
        }

        if storage_info is not None:
            result["object_storage"] = storage_info

        return result

    finally:
        client.close()
