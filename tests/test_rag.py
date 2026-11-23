from app.services import rag


def make_chunk(
    distance=0.4,
    chunk_id="chunk-1",
    document_id="document-1",
    chunk_index=0,
    text="Фрагмент клинических рекомендаций"
):
    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "chunk_index": chunk_index,
        "chunk_text": text,
        "page_number": 1,
        "token_count": 20,
        "distance": distance
    }


def test_ask_rag_generates_answer_from_relevant_chunks(monkeypatch):
    chunks = [
        make_chunk(distance=0.4),
        make_chunk(
            distance=0.6,
            chunk_id="chunk-2",
            chunk_index=1,
            text="Дополнительный релевантный фрагмент"
        ),
        make_chunk(
            distance=0.9,
            chunk_id="chunk-3",
            chunk_index=2,
            text="Нерелевантный фрагмент"
        )
    ]

    monkeypatch.setattr(rag, "search_chunks", lambda *args, **kwargs: chunks)

    def fake_generate(question, context):
        assert question == "Как диагностировать заболевание?"
        assert "Фрагмент клинических рекомендаций" in context
        assert "Дополнительный релевантный фрагмент" in context
        assert "Нерелевантный фрагмент" not in context
        return "Ответ на основе клинических рекомендаций"

    monkeypatch.setattr(rag, "generate_answer", fake_generate)

    logged = {}
    monkeypatch.setattr(
        rag,
        "log_query",
        lambda **kwargs: logged.update(kwargs)
    )

    result = rag.ask_rag("Как диагностировать заболевание?")

    assert result["question"] == "Как диагностировать заболевание?"
    assert result["answer"] == "Ответ на основе клинических рекомендаций"
    assert result["insufficient_data"] is False
    assert result["retrieved_chunks"] == 2
    assert len(result["sources"]) == 2
    assert result["response_time_ms"] >= 0

    assert logged["insufficient_data"] is False
    assert logged["retrieved_chunks"] == 2


def test_ask_rag_returns_insufficient_data_when_no_chunks(monkeypatch):
    monkeypatch.setattr(
        rag,
        "search_chunks",
        lambda *args, **kwargs: []
    )

    def unexpected_generation(*args, **kwargs):
        raise AssertionError("GigaChat не должен вызываться")

    monkeypatch.setattr(
        rag,
        "generate_answer",
        unexpected_generation
    )

    logged = {}
    monkeypatch.setattr(
        rag,
        "log_query",
        lambda **kwargs: logged.update(kwargs)
    )

    result = rag.ask_rag("Вопрос без найденных фрагментов")

    assert result["insufficient_data"] is True
    assert result["sources"] == []
    assert result["retrieved_chunks"] == 0
    assert "Недостаточно релевантной информации" in result["answer"]
    assert logged["insufficient_data"] is True


def test_ask_rag_filters_chunks_by_distance(monkeypatch):
    chunks = [
        make_chunk(distance=0.69),
        make_chunk(
            distance=0.71,
            chunk_id="chunk-2",
            chunk_index=1
        )
    ]

    monkeypatch.setattr(
        rag,
        "search_chunks",
        lambda *args, **kwargs: chunks
    )

    monkeypatch.setattr(
        rag,
        "generate_answer",
        lambda question, context: "Ответ"
    )

    monkeypatch.setattr(rag, "log_query", lambda **kwargs: None)

    result = rag.ask_rag("Проверка порога релевантности")

    assert result["insufficient_data"] is False
    assert result["retrieved_chunks"] == 1
    assert len(result["sources"]) == 1
    assert result["sources"][0]["distance"] == 0.69


def test_ask_rag_passes_top_k_to_retrieval(monkeypatch):
    received = {}

    def fake_search(question, top_k):
        received["question"] = question
        received["top_k"] = top_k
        return []

    monkeypatch.setattr(rag, "search_chunks", fake_search)
    monkeypatch.setattr(rag, "log_query", lambda **kwargs: None)

    result = rag.ask_rag("Тест передачи параметров", top_k=8)

    assert received["question"] == "Тест передачи параметров"
    assert received["top_k"] == 8
    assert result["insufficient_data"] is True


def test_ask_rag_propagates_generation_error(monkeypatch):
    monkeypatch.setattr(
        rag,
        "search_chunks",
        lambda *args, **kwargs: [make_chunk()]
    )

    def fail_generation(*args, **kwargs):
        raise RuntimeError("Ошибка генерации")

    monkeypatch.setattr(rag, "generate_answer", fail_generation)
    monkeypatch.setattr(rag, "log_query", lambda **kwargs: None)

    import pytest

    with pytest.raises(RuntimeError, match="Ошибка генерации"):
        rag.ask_rag("Проверка ошибки генерации")
