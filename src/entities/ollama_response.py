from typing import Optional
from pydantic import BaseModel

class OllamaResponse(BaseModel):
    thought_process: Optional[str]
    response: str
