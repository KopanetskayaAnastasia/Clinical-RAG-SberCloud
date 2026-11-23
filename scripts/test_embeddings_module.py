import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.embeddings import create_embedding

text = (
    "Клинические рекомендации Минздрава РФ "
    "по диагностике и лечению артериальной гипертензии."
)

print("[1] Отправка медицинского текста в Cloud.ru")
vector = create_embedding(text)

print("[2] Эмбеддинг успешно получен")
print("Размерность:", len(vector))
print("Первые 5 значений:", vector[:5])

print("\nУСПЕХ: модуль эмбеддингов работает")
