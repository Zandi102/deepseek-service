
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from dependency_injector.wiring import inject
from src.entities.deep_seek_request import DeepSeekRequest

router = APIRouter()

@cbv(router)
class DeepSeekRouter:
    
    @router.post("/deepseek/generate")
    async def generate_response(self, request: DeepSeekRequest):
        try:
            return {request.role: request.message}
        
        except Exception:
            raise
