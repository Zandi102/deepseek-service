
import asyncio
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from src.entities.ollama_response import OllamaResponse
import ollama
import re
import speech_recognition as sr
import pyttsx3
from pydantic import BaseModel
from http_status import Status

router = APIRouter()

class SpeechInput(BaseModel):
    text: str

@cbv(router)
class DeepSeekRouter:
    def __init__(self):
        self.model_version = "deepseek-r1:1.5b"        
    
    async def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    @router.post('/alix')  # 🔹 Change GET to POST
    async def begin_ai_integration(self, input_data: SpeechInput):  
        user_input = input_data.text  # 🔹 Get user input from request

        if not user_input:
            return Status(code=400, name_fail="No input", description_fail="No input received from user")

        try:
            response_stream = await asyncio.to_thread(
                ollama.chat,
                model="deepseek-r1:1.5b",
                messages=[{'role': 'user', 'content': user_input}],
                stream=False
            )

            full_response = response_stream.message.content

            thoughts = re.search(r"<think>(.*?)</think>", full_response, re.DOTALL)
            ai_thoughts = thoughts.group(1).strip().replace('\n', '') if thoughts else ""

            ai_response = re.search(r"</think>\s*(.*)", full_response, re.DOTALL)
            ai_response = ai_response.group(1).strip().replace('\n', '') if ai_response else ""

            ollama_response = OllamaResponse(thought_process=ai_thoughts, response=ai_response)

            return {"response": ollama_response.response, "thoughts": ai_thoughts}  # 🔹 Return response for frontend to display
            
        except Exception as ex:
            print(f"Error in AI response: {str(ex)}")
            return Status(code=400, name_fail="AI Generation Exception", description_fail=f"Failure to generate AI response due to error {str(ex)}")

    
