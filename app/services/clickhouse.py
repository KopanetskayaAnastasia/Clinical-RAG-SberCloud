
import os
import time

import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()


def get_clickhouse_client():
    app_env = os.getenv("APP_ENV", "development").strip().lower()
    is_production = app_env in {"production", "prod"}

    host = os.getenv("CLICKHOUSE_HOST")

    if not host:
        if is_production:
            raise ValueError(
                "В облачном режиме необходимо задать CLICKHOUSE_HOST"
            )
        host = "127.0.0.1"

    port_value = os.getenv("CLICKHOUSE_PORT")

    if not port_value:
        if is_production:
            raise ValueError(
                "В облачном режиме необходимо задать CLICKHOUSE_PORT"
            )
        port_value = "8123"

    try:
        port = int(port_value)
    except ValueError:
        raise ValueError("CLICKHOUSE_PORT должен быть числом")

    username = (
        os.getenv("CLICKHOUSE_USER")
        if is_production
        else os.getenv("CLICKHOUSE_USER", "rag_user")
    )

    password = os.getenv("CLICKHOUSE_PASSWORD")
    database = os.getenv("CLICKHOUSE_DATABASE", "clinical_rag")

    if not username:
        raise ValueError("Не задан CLICKHOUSE_USER")

    if not password:
        raise ValueError("Не задан CLICKHOUSE_PASSWORD")

    secure_value = os.getenv("CLICKHOUSE_SECURE")

    if is_production and secure_value is None:
        raise ValueError(
            "Для облачного режима явно задайте CLICKHOUSE_SECURE=true или false"
        )

    secure = (
        secure_value.strip().lower() in {"true", "1", "yes"}
        if secure_value is not None
        else False
    )

    return clickhouse_connect.get_client(
        host=host,
        port=port,
        username=username,
        password=password,
        database=database,
        secure=secure,
        connect_timeout=10,
        send_receive_timeout=60
    )


def initialize_tables():
    """Создаёт таблицы Clinical RAG, если они ещё не существуют."""

    client = None

    for attempt in range(1, 16):
        try:
            client = get_clickhouse_client()
            break
        except Exception:
            if attempt == 15:
                raise
            time.sleep(2)

    try:
        client.command("""
            CREATE TABLE IF NOT EXISTS documents
            (
                document_id UUID DEFAULT generateUUIDv4(),
                filename String,
                title String,
                source String,
                document_type String DEFAULT 'clinical_guideline',
                publication_date Nullable(Date),
                version String DEFAULT '',
                uploaded_at DateTime DEFAULT now(),
                total_chunks UInt32 DEFAULT 0,
                status String DEFAULT 'processed'
            )
            ENGINE = MergeTree
            ORDER BY (filename, uploaded_at)
            SETTINGS index_granularity = 8192
        """)

        client.command("""
            CREATE TABLE IF NOT EXISTS document_chunks
            (
                chunk_id UUID DEFAULT generateUUIDv4(),
                document_id UUID,
                chunk_index UInt32,
                chunk_text String,
                page_number Nullable(UInt32),
                token_count UInt32 DEFAULT 0,
                embedding Array(Float32),
                created_at DateTime DEFAULT now()
            )
            ENGINE = MergeTree
            ORDER BY (document_id, chunk_index)
            SETTINGS index_granularity = 8192
        """)

        client.command("""
            CREATE TABLE IF NOT EXISTS query_logs
            (
                log_id UUID DEFAULT generateUUIDv4(),
                user_query String,
                generated_answer String DEFAULT '',
                retrieved_chunks UInt32 DEFAULT 0,
                relevance_score Nullable(Float32),
                insufficient_data UInt8 DEFAULT 0,
                response_time_ms UInt32 DEFAULT 0,
                created_at DateTime DEFAULT now()
            )
            ENGINE = MergeTree
            ORDER BY (created_at, log_id)
            SETTINGS index_granularity = 8192
        """)

        return {
            "status": "initialized",
            "tables": [
                "documents",
                "document_chunks",
                "query_logs"
            ]
        }

    finally:
        if client is not None:
            client.close()


def check_connection():
    client = get_clickhouse_client()

    try:
        result = client.query("""
            SELECT
                version(),
                currentDatabase()
        """)

        return {
            "version": result.result_rows[0][0],
            "database": result.result_rows[0][1]
        }
    finally:
        client.close()
