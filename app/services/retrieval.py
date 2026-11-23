from app.services.embeddings import create_embedding, EXPECTED_DIMENSION
from app.services.clickhouse import get_clickhouse_client


def search_chunks(query: str, top_k: int = 5) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("Поисковый запрос не должен быть пустым")

    if not 1 <= top_k <= 100:
        raise ValueError("top_k должен находиться в диапазоне от 1 до 100")

    print("[1] Векторизация поискового запроса")
    query_vector = create_embedding(query)

    if len(query_vector) != EXPECTED_DIMENSION:
        raise ValueError("Некорректная размерность поискового вектора")

    print("[2] Поиск в ClickHouse")

    client = get_clickhouse_client()

    try:
        result = client.query(
            """
            SELECT
                chunk_id,
                document_id,
                chunk_index,
                chunk_text,
                page_number,
                token_count,
                cosineDistance(
                    embedding,
                    {query_embedding:Array(Float32)}
                ) AS distance
            FROM document_chunks
            ORDER BY distance ASC
            LIMIT {limit:UInt32}
            """,
            parameters={
                "query_embedding": query_vector,
                "limit": top_k
            }
        )

        return [
            {
                "chunk_id": str(row[0]),
                "document_id": str(row[1]),
                "chunk_index": row[2],
                "chunk_text": row[3],
                "page_number": row[4],
                "token_count": row[5],
                "distance": float(row[6])
            }
            for row in result.result_rows
        ]

    finally:
        client.close()
