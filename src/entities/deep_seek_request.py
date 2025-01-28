from pydantic import BaseModel

class DeepSeekRequest(BaseModel):
    role: str
    message: str