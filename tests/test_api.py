import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import search as search_api
from app.api import chat as chat_api


client = TestClient(app)


def test_search_endpoint_success(monkeypatch):
    fake_results = [
        {
            "chunk_id": "chunk-1",
            "document_id": "document-1",
            "chunk_index": 0,
            "chunk_text": "Фрагмент клинических рекомендаций",
            "page_number": 1,
            "token_count": 20,
            "distance": 0.35
        }
    ]

    monkeypatch.setattr(
        search_api,
        "search_chunks",
        lambda query, top_k: fake_results
    )

    response = client.post(
        "/search/",
        json={
            "query": "Диагностика заболевания",
            "top_k": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "Диагностика заболевания"
    assert data["results_count"] == 1
    assert data["results"][0]["chunk_id"] == "chunk-1"


def test_search_endpoint_rejects_short_query():
    response = client.post(
        "/search/",
        json={"query": "А"}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("top_k", [0, 21, -1])
def test_search_endpoint_rejects_invalid_top_k(top_k):
    response = client.post(
        "/search/",
        json={
            "query": "Тестовый запрос",
            "top_k": top_k
        }
    )

    assert response.status_code == 422


def test_search_endpoint_handles_internal_error(monkeypatch):
    def fail_search(*args, **kwargs):
        raise RuntimeError("Test search error")

    monkeypatch.setattr(
        search_api,
        "search_chunks",
        fail_search
    )

    response = client.post(
        "/search/",
        json={"query": "Тестовый запрос"}
    )

    assert response.status_code == 500


def test_chat_endpoint_success(monkeypatch):
    fake_result = {
        "question": "Как диагностировать заболевание?",
        "answer": "Ответ на основе клинических рекомендаций",
        "sources": [
            {
                "document_id": "document-1",
                "chunk_id": "chunk-1",
                "chunk_index": 0,
                "text": "Фрагмент рекомендаций",
                "distance": 0.35
            }
        ],
        "retrieved_chunks": 1,
        "insufficient_data": False,
        "response_time_ms": 150
    }

    monkeypatch.setattr(
        chat_api,
        "ask_rag",
        lambda question, top_k: fake_result
    )

    response = client.post(
        "/chat/",
        json={
            "question": "Как диагностировать заболевание?",
            "top_k": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == fake_result["answer"]
    assert data["insufficient_data"] is False
    assert len(data["sources"]) == 1
    assert data["retrieved_chunks"] == 1


def test_chat_endpoint_rejects_short_question():
    response = client.post(
        "/chat/",
        json={"question": "А"}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("top_k", [0, 21, -1])
def test_chat_endpoint_rejects_invalid_top_k(top_k):
    response = client.post(
        "/chat/",
        json={
            "question": "Тестовый вопрос",
            "top_k": top_k
        }
    )

    assert response.status_code == 422


def test_chat_endpoint_handles_internal_error(monkeypatch):
    def fail_rag(*args, **kwargs):
        raise RuntimeError("Test RAG error")

    monkeypatch.setattr(
        chat_api,
        "ask_rag",
        fail_rag
    )

    response = client.post(
        "/chat/",
        json={"question": "Тестовый вопрос"}
    )

    assert response.status_code == 500
