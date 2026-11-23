from app.services.chunker import (
    count_tokens,
    split_into_sentences,
    chunk_text,
    chunk_document,
)


def test_count_tokens_returns_positive_number():
    result = count_tokens("Клинические рекомендации")

    assert isinstance(result, int)
    assert result > 0


def test_split_into_sentences():
    text = "Первое предложение. Второе предложение! Третье предложение?"

    result = split_into_sentences(text)

    assert len(result) == 3
    assert result[0] == "Первое предложение."
    assert result[1] == "Второе предложение!"
    assert result[2] == "Третье предложение?"


def test_split_into_sentences_handles_empty_text():
    assert split_into_sentences("") == []


def test_chunk_text_returns_expected_structure():
    result = chunk_text(
        "Клинические рекомендации содержат информацию о диагностике и лечении.",
        page_number=1
    )

    assert len(result) == 1
    assert result[0]["chunk_text"]
    assert result[0]["page_number"] == 1
    assert result[0]["token_count"] > 0


def test_chunk_text_handles_empty_text():
    assert chunk_text("") == []


def test_chunk_document_assigns_sequential_indexes():
    pages = [
        {
            "page_number": 1,
            "text": "Первая страница содержит клиническую информацию."
        },
        {
            "page_number": 2,
            "text": "Вторая страница содержит информацию о лечении."
        }
    ]

    result = chunk_document(pages)

    assert len(result) == 2
    assert result[0]["chunk_index"] == 0
    assert result[1]["chunk_index"] == 1
    assert result[0]["page_number"] == 1
    assert result[1]["page_number"] == 2


def test_chunk_document_handles_empty_pages():
    assert chunk_document([]) == []
