import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.ingestion import ingest_document
from app.services.object_storage import upload_file_to_storage


router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    raw_filename = (file.filename or "document").replace("\\", "/")
    filename = Path(raw_filename).name
    extension = Path(filename).suffix.lower()

    if not filename or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только форматы PDF, DOCX и TXT"
        )

    temp_path = None
    storage_result = None

    try:
        # 1. Временно сохраняем загруженный файл
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:
            temp_path = Path(temp_file.name)
            shutil.copyfileobj(file.file, temp_file)

        # 2. Формируем уникальный ключ объекта в Cloud.ru
        object_name = f"documents/{uuid4().hex}/{filename}"

        # 3. Сохраняем оригинал в Cloud.ru Object Storage
        try:
            storage_result = upload_file_to_storage(
                str(temp_path),
                object_name=object_name
            )
        except Exception as error:
            print(f"Ошибка загрузки в Object Storage: {error}")

            raise HTTPException(
                status_code=502,
                detail="Не удалось сохранить документ в Cloud.ru Object Storage"
            )

        # 4. Обрабатываем документ и записываем фрагменты
        #    и эмбеддинги в ClickHouse
        try:
            result = ingest_document(
                str(temp_path),
                filename=filename,
                storage_info=storage_result
            )
        except Exception as error:
            print(f"Ошибка обработки документа: {error}")

            raise HTTPException(
                status_code=500,
                detail={
                    "message": (
                        "Документ сохранён в Object Storage, "
                        "но его обработка не завершена"
                    ),
                    "object_storage": storage_result
                }
            )

        # 5. Возвращаем результат
        return {
            "message": "Документ сохранён и обработан",
            "filename": filename,
            "object_storage": storage_result,
            "result": result
        }

    except HTTPException:
        raise

    except Exception as error:
        print(f"Ошибка загрузки документа: {error}")

        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка при загрузке документа"
        )

    finally:
        await file.close()

        if temp_path and temp_path.exists():
            temp_path.unlink()
