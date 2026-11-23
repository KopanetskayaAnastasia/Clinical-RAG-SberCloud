
from app.services.clickhouse import get_clickhouse_client


def log_query(
    user_query: str,
    generated_answer: str,
    retrieved_chunks: int,
    insufficient_data: bool,
    response_time_ms: int,
    relevance_score: float | None = None
) -> None:
    """
    Сохраняет информацию о запросе и ответе RAG-системы
    в таблице query_logs ClickHouse.
    """

    client = get_clickhouse_client()

    try:
        client.insert(
            "query_logs",
            [[
                user_query,
                generated_answer,
                retrieved_chunks,
                relevance_score,
                int(insufficient_data),
                response_time_ms
            ]],
            column_names=[
                "user_query",
                "generated_answer",
                "retrieved_chunks",
                "relevance_score",
                "insufficient_data",
                "response_time_ms"
            ]
        )
    finally:
        client.close()
