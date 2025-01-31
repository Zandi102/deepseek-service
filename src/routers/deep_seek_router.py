
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from src.entities.ollama_response import OllamaResponse
from src.entities.deep_seek_request import DeepSeekRequest
import ollama
import re

router = APIRouter()

@cbv(router)
class DeepSeekRouter:
    def __init__(self):
        self.model_version = "deepseek-r1:14b"
    
    @router.post("/deepseek/generate")
    async def generate_response(self, request: DeepSeekRequest) -> OllamaResponse:
        try:
            response_object = ollama.chat(model=self.model_version, 
                                          messages=[
                                              {'role': request.role, 
                                               'content': request.message},
                                          ])
            
            if not response_object: 
                raise LookupError(f'Unable to retrieve ollama response from model: {self.model_version}')
            
            thoughts = re.search(r"<think>(.*?)</think>", 
                                 response_object.message.content, 
                                 re.DOTALL)
            
            ai_thoughts = thoughts.group(1).strip().replace('\n', '') \
                if thoughts else ""

            ai_response = re.search(r"</think>\s*(.*)",
                                    response_object.message.content,
                                    re.DOTALL)
            
            ai_response = ai_response.group(1).strip().replace('\n', '') \
                if ai_response else ""
            
            return OllamaResponse(thought_process=ai_thoughts, 
                                  response=ai_response)
        
        except Exception as ex:
            print(str(ex))
            raise ex
