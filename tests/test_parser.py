import pytest
from docx import Document

from app.services.parser import parse_document


def test_parse_txt(tmp_path):
    file_path = tmp_path / "guideline.txt"
    file_path.write_text(
        "Клинические рекомендации по диагностике и лечению.",
        encoding="utf-8"
    )

    result = parse_document(str(file_path))

    assert len(result) == 1
    assert result[0]["page_number"] is None
    assert "Клинические рекомендации" in result[0]["text"]


def test_parse_txt_with_utf8_bom(tmp_path):
    file_path = tmp_path / "guideline.txt"
    file_path.write_text(
        "Текст документа с BOM.",
        encoding="utf-8-sig"
    )

    result = parse_document(str(file_path))

    assert len(result) == 1
    assert result[0]["text"] == "Текст документа с BOM."


def test_parse_docx(tmp_path):
    file_path = tmp_path / "guideline.docx"

    document = Document()
    document.add_paragraph("Первый раздел клинических рекомендаций.")
    document.add_paragraph("Второй раздел содержит сведения о лечении.")
    document.save(file_path)

    result = parse_document(str(file_path))

    assert len(result) == 1
    assert result[0]["page_number"] is None
    assert "Первый раздел" in result[0]["text"]
    assert "Второй раздел" in result[0]["text"]


def test_parse_pdf(tmp_path):
    pytest.importorskip("reportlab.pdfgen")

    from reportlab.pdfgen import canvas

    file_path = tmp_path / "guideline.pdf"

    pdf = canvas.Canvas(str(file_path))
    pdf.drawString(72, 750, "Clinical recommendations")
    pdf.drawString(72, 730, "Diagnosis and treatment")
    pdf.save()

    result = parse_document(str(file_path))

    assert len(result) == 1
    assert result[0]["page_number"] == 1
    assert "Clinical recommendations" in result[0]["text"]


def test_parse_missing_file():
    with pytest.raises(FileNotFoundError):
        parse_document("missing_document.txt")


def test_parse_unsupported_format(tmp_path):
    file_path = tmp_path / "document.xlsx"
    file_path.write_text("Test", encoding="utf-8")

    with pytest.raises(ValueError, match="Неподдерживаемый формат"):
        parse_document(str(file_path))


def test_parse_empty_txt(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("   \n  ", encoding="utf-8")

    with pytest.raises(ValueError, match="Не удалось извлечь текст"):
        parse_document(str(file_path))
