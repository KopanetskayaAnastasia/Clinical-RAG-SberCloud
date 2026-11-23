
import time

from app.services.retrieval import search_chunks
from app.services.gigachat import generate_answer
from app.services.logging import log_query


# Предварительный экспериментальный порог косинусного расстояния
MAX_DISTANCE = 0.70


def ask_rag(question: str, top_k: int = 5) -> dict:
    start_time = time.perf_counter()

    print("[1] Поиск релевантных фрагментов")
    chunks = search_chunks(question, top_k=top_k)

    # Отбираем только фрагменты, прошедшие порог релевантности
    relevant_chunks = [
        chunk for chunk in chunks
        if chunk["distance"] <= MAX_DISTANCE
    ]

    if not relevant_chunks:
        print("[2] Недостаточно релевантных данных")

        answer = (
            "Недостаточно релевантной информации в загруженных "
            "документах для ответа на данный вопрос. "
            "Обратитесь к полным клиническим рекомендациям."
        )

        response_time_ms = round(
            (time.perf_counter() - start_time) * 1000
        )

        log_query(
            user_query=question,
            generated_answer=answer,
            retrieved_chunks=len(chunks),
            insufficient_data=True,
            response_time_ms=response_time_ms
        )

        return {
            "question": question,
            "answer": answer,
            "sources": [],
            "retrieved_chunks": len(chunks),
            "insufficient_data": True,
            "response_time_ms": response_time_ms
        }

    print("[2] Формирование контекста")

    context_parts = []

    for index, chunk in enumerate(relevant_chunks, start=1):
        context_parts.append(
            f"[Источник {index}]\n"
            f"Документ ID: {chunk['document_id']}\n"
            f"Фрагмент: {chunk['chunk_text']}"
        )

    context = "\n\n".join(context_parts)

    print("[3] Генерация ответа GigaChat")
    answer = generate_answer(question, context)

    sources = [
        {
            "document_id": chunk["document_id"],
            "chunk_id": chunk["chunk_id"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["chunk_text"],
            "distance": chunk["distance"]
        }
        for chunk in relevant_chunks
    ]

    response_time_ms = round(
        (time.perf_counter() - start_time) * 1000
    )

    log_query(
        user_query=question,
        generated_answer=answer,
        retrieved_chunks=len(relevant_chunks),
        insufficient_data=False,
        response_time_ms=response_time_ms
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": len(relevant_chunks),
        "insufficient_data": False,
        "response_time_ms": response_time_ms
    }
