import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.clickhouse import (
    get_clickhouse_client,
    check_connection
)

print("[1] Проверка модуля подключения")

info = check_connection()

print("Версия ClickHouse:", info["version"])
print("База данных:", info["database"])

print("\n[2] Проверка таблиц")

client = get_clickhouse_client()

try:
    result = client.query("SHOW TABLES")

    for row in result.result_rows:
        print("-", row[0])

    print("\nУСПЕХ: модуль ClickHouse работает")

finally:
    client.close()
