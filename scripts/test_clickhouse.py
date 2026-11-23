import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

password = os.getenv("CLICKHOUSE_PASSWORD")

if not password:
    raise ValueError("Не найден CLICKHOUSE_PASSWORD в файле .env")

print("[1] Подключение к ClickHouse...")

client = clickhouse_connect.get_client(
    host="127.0.0.1",
    port=8123,
    username="rag_user",
    password=password,
    database="clinical_rag"
)

print("[2] Проверка подключения...")

result = client.query(
    "SELECT version(), currentDatabase()"
)

print("\nУСПЕХ: Python подключился к ClickHouse")
print("Версия:", result.result_rows[0][0])
print("База данных:", result.result_rows[0][1])

client.close()
