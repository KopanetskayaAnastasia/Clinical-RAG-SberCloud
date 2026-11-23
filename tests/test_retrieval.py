from unittest.mock import Mock

import pytest

from app.services import retrieval


def test_search_chunks_rejects_empty_query():
    with pytest.raises(ValueError, match="не должен быть пустым"):
        retrieval.search_chunks("")


def test_search_chunks_rejects_whitespace_query():
    with pytest.raises(ValueError, match="не должен быть пустым"):
        retrieval.search_chunks("   ")


@pytest.mark.parametrize("top_k", [0, -1, 101])
def test_search_chunks_rejects_invalid_top_k(top_k):
    with pytest.raises(ValueError, match="top_k"):
        retrieval.search_chunks("тестовый запрос", top_k)


def test_search_chunks_returns_results(monkeypatch):
    expected_vector = [0.1] * retrieval.EXPECTED_DIMENSION

    fake_row = (
        "chunk-1",
        "document-1",
        0,
        "Фрагмент клинических рекомендаций",
        1,
        12,
        0.25
    )

    fake_client = Mock()
    fake_client.query.return_value.result_rows = [fake_row]

    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        lambda query: expected_vector
    )
    monkeypatch.setattr(
        retrieval,
        "get_clickhouse_client",
        lambda: fake_client
    )

    result = retrieval.search_chunks("диагностика")

    assert len(result) == 1
    assert result[0]["chunk_id"] == "chunk-1"
    assert result[0]["document_id"] == "document-1"
    assert result[0]["chunk_index"] == 0
    assert result[0]["chunk_text"] == "Фрагмент клинических рекомендаций"
    assert result[0]["page_number"] == 1
    assert result[0]["token_count"] == 12
    assert result[0]["distance"] == 0.25

    fake_client.query.assert_called_once()
    fake_client.close.assert_called_once()


def test_search_chunks_rejects_wrong_embedding_dimension(monkeypatch):
    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        lambda query: [0.1, 0.2]
    )

    with pytest.raises(ValueError, match="размерность"):
        retrieval.search_chunks("диагностика")


def test_search_chunks_closes_client_after_query_error(monkeypatch):
    fake_client = Mock()
    fake_client.query.side_effect = RuntimeError("Ошибка ClickHouse")

    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        lambda query: [0.1] * retrieval.EXPECTED_DIMENSION
    )
    monkeypatch.setattr(
        retrieval,
        "get_clickhouse_client",
        lambda: fake_client
    )

    with pytest.raises(RuntimeError, match="Ошибка ClickHouse"):
        retrieval.search_chunks("диагностика")

    fake_client.close.assert_called_once()


def test_search_chunks_returns_empty_list_when_no_matches(monkeypatch):
    fake_client = Mock()
    fake_client.query.return_value.result_rows = []

    monkeypatch.setattr(
        retrieval,
        "create_embedding",
        lambda query: [0.1] * retrieval.EXPECTED_DIMENSION
    )
    monkeypatch.setattr(
        retrieval,
        "get_clickhouse_client",
        lambda: fake_client
    )

    result = retrieval.search_chunks("редкий запрос")

    assert result == []
    fake_client.close.assert_called_once()
