from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image
import io
import base64

from src.search import DocumentSearchService

# Инициализация роутера и сервиса
search_router = APIRouter(prefix="/search", tags=["search"])
search_service = DocumentSearchService()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 2

class ResponseGenerationRequest(BaseModel):
    query: str
    image_base64: str

@search_router.post("/documents")
async def search_documents(request: SearchRequest):
    """
    Эндпоинт для поиска документов
    """
    try:
        result = search_service.search_documents(
            request.query, 
            request.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@search_router.post("/generate-response")
async def generate_response(request: ResponseGenerationRequest):
    """
    Эндпоинт для генерации ответа по изображению
    """
    try:
        # Декодируем base64 изображение
        image_bytes = base64.b64decode(request.image_base64)
        image = Image.open(io.BytesIO(image_bytes))

        # Генерируем ответ
        response = search_service.generate_response(
            request.query, 
            image
        )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
