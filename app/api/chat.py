
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag import ask_rag


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        description="Вопрос по медицинским документам"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Количество извлекаемых фрагментов"
    )


@router.post("/")
def chat(request: ChatRequest):
    try:
        result = ask_rag(
            question=request.question,
            top_k=request.top_k
        )
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка обработки запроса: {str(error)}"
        )
