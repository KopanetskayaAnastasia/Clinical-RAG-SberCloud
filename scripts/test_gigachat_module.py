import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.gigachat import generate_answer

print("=== ТЕСТ МОДУЛЯ GIGACHAT ===")

question = "Что содержат клинические рекомендации?"

context = (
    "Клинические рекомендации содержат сведения о диагностике, "
    "профилактике и лечении заболеваний."
)

print("[1] Отправка запроса в GigaChat")

answer = generate_answer(question, context)

print("\n=== ОТВЕТ GIGACHAT ===")
print(answer)

if answer and answer.strip():
    print("\nУСПЕХ: модуль GigaChat работает")
else:
    print("\nОШИБКА: получен пустой ответ")
