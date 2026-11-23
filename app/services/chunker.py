import re
import tiktoken

ENCODING = tiktoken.get_encoding("cl100k_base")

TARGET_TOKENS = 700
MAX_TOKENS = 1000
OVERLAP_TOKENS = 100


def count_tokens(text: str) -> int:
    return len(ENCODING.encode(text))


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def chunk_text(text: str, page_number: int | None = None) -> list[dict]:
    sentences = split_into_sentences(text)

    chunks = []
    current_sentences = []
    current_tokens = 0

    def save_chunk():
        if not current_sentences:
            return

        chunk = " ".join(current_sentences).strip()

        chunks.append({
            "chunk_text": chunk,
            "page_number": page_number,
            "token_count": count_tokens(chunk)
        })

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        if sentence_tokens > MAX_TOKENS:
            if current_sentences:
                save_chunk()
                current_sentences = []
                current_tokens = 0

            tokens = ENCODING.encode(sentence)

            for start in range(0, len(tokens), MAX_TOKENS - OVERLAP_TOKENS):
                part = ENCODING.decode(
                    tokens[start:start + MAX_TOKENS]
                ).strip()

                if part:
                    chunks.append({
                        "chunk_text": part,
                        "page_number": page_number,
                        "token_count": count_tokens(part)
                    })

            continue

        if (
            current_tokens + sentence_tokens > TARGET_TOKENS
            and current_sentences
        ):
            save_chunk()

            overlap = []
            overlap_count = 0

            for old_sentence in reversed(current_sentences):
                old_tokens = count_tokens(old_sentence)

                if overlap_count + old_tokens > OVERLAP_TOKENS:
                    break

                overlap.insert(0, old_sentence)
                overlap_count += old_tokens

            current_sentences = overlap
            current_tokens = overlap_count

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    save_chunk()

    return chunks


def chunk_document(pages: list[dict]) -> list[dict]:
    result = []

    for page in pages:
        page_chunks = chunk_text(
            page["text"],
            page.get("page_number")
        )
        result.extend(page_chunks)

    for index, chunk in enumerate(result):
        chunk["chunk_index"] = index

    return result
