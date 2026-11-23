
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.retrieval import search_chunks


router = APIRouter(prefix="/search", tags=["Search"])


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        description="Поисковый запрос"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Количество возвращаемых фрагментов"
    )


@router.post("/")
def search(request: SearchRequest):
    try:
        chunks = search_chunks(
            query=request.query,
            top_k=request.top_k
        )

        return {
            "query": request.query,
            "results_count": len(chunks),
            "results": chunks
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка семантического поиска: {str(error)}"
        )
