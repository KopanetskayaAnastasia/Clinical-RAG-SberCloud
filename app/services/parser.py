from pathlib import Path
from pypdf import PdfReader
from docx import Document


def parse_document(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    extension = path.suffix.lower()
    pages = []

    if extension == ".pdf":
        reader = PdfReader(str(path))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                pages.append({
                    "page_number": page_number,
                    "text": text.strip()
                })

    elif extension == ".docx":
        document = Document(str(path))

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        if text.strip():
            pages.append({
                "page_number": None,
                "text": text.strip()
            })

    elif extension == ".txt":
        try:
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            text = path.read_text(encoding="cp1251")

        if text.strip():
            pages.append({
                "page_number": None,
                "text": text.strip()
            })

    else:
        raise ValueError(
            f"Неподдерживаемый формат: {extension}. "
            "Допустимы PDF, DOCX и TXT."
        )

    if not pages:
        raise ValueError(
            "Не удалось извлечь текст. "
            "Возможно, PDF содержит только изображения."
        )

    return pages
