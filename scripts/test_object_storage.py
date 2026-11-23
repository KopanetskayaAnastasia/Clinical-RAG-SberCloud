from botocore.exceptions import ClientError
from app.services.object_storage import check_storage_connection

if __name__ == "__main__":
    try:
        result = check_storage_connection()

        print("=== CLOUD.RU OBJECT STORAGE ===")
        print("Подключение успешно!")
        print("Бакет:", result["bucket"])
        print("Статус:", result["status"])
        print("Тестовый объект:", result["test_object"])

    except ClientError as error:
        print("=== ОШИБКА CLOUD.RU OBJECT STORAGE ===")

        response = error.response
        details = response.get("Error", {})

        print("Код ошибки:", details.get("Code"))
        print("Сообщение:", details.get("Message"))
        print("HTTP:", response.get("ResponseMetadata", {}).get("HTTPStatusCode"))
        print("Request ID:", response.get("ResponseMetadata", {}).get("RequestId"))

    except Exception as error:
        print("Ошибка:", type(error).__name__)
        print(str(error))