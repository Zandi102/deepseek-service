
import asyncio
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from src.entities.ollama_response import OllamaResponse
import ollama
import re
import speech_recognition as sr
import pyttsx3
from http_status import Status

router = APIRouter()

@cbv(router)
class DeepSeekRouter:
    def __init__(self):
        self.model_version = "deepseek-r1:1.5b"        
    
    async def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    async def listen(self, max_attempts=2, timeout=15) -> str:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            attempts = 0
            while attempts < max_attempts:
                try:
                    print("Listening... Speak now!")
                    audio = recognizer.listen(source, timeout=timeout)
                    text = recognizer.recognize_google(audio)
                    print("You said:", text)
                    return text
                
                except sr.UnknownValueError:
                    print("Could not understand the audio, retrying...")
                    recognizer.pause_threshold = float('inf')
                    await self.speak("Sorry, I couldn't understand that, please repeat.") if attempts != 1 else await self.speak("Goodbye, Alex")
                    recognizer.pause_threshold = 1
                except sr.RequestError:
                    print("Speech recognition service is unavailable, retrying...")
                    recognizer.pause_threshold = float('inf')
                    await self.speak("Sorry, the speech recognition service is unavailable.") if attempts != 1 else await self.speak("Goodbye, Alex")
                    recognizer.pause_threshold = 1
                except Exception:
                    print(f"Error during listening")
                    recognizer.pause_threshold = float('inf')
                    await self.speak("Sorry, there was an error, please try again.") if attempts != 1 else await self.speak("Goodbye, Alex")
                    recognizer.pause_threshold = 1
                
                attempts += 1

            raise Exception("User did not respond")
        

    @router.get('/alix')
    async def begin_ai_integration(self):    
        try:
            user_input = await self.listen()

            for command in ["alex exit", "alex quit", "alex stop"]:
                if command in user_input.lower():
                    await self.speak("Goodbye Alex!")
                    return
                        
        except Exception as ex:
            return Status(code=400, name_fail="SpeechRecognition Listener Exception", description_fail=f"Failure during listening process due to Exception {str(ex)}")
        
        try:
            response_stream = await asyncio.to_thread(
                ollama.chat,
                model=self.model_version,
                messages=[{'role': 'user', 'content': user_input}],
                stream=False
            )

            full_response = response_stream.message.content

            thoughts = re.search(r"<think>(.*?)</think>", full_response, re.DOTALL)
            ai_thoughts = thoughts.group(1).strip().replace('\n', '') if thoughts else ""

            ai_response = re.search(r"</think>\s*(.*)", full_response, re.DOTALL)
            ai_response = ai_response.group(1).strip().replace('\n', '') if ai_response else ""

            ollama_response = OllamaResponse(thought_process=ai_thoughts, response=ai_response)
            
            await self.speak(ollama_response.response) 
            
            return Status(code=200, name_fail=None, description_fail=None)
            
        except Exception as ex:
            print(f"Error in AI response: {str(ex)}")
            await self.speak("Sorry, I encountered an issue processing your request.")
            return Status(code=400, name_fail="AI Generation Exception", description_fail=f"Failure to generate AI response due to error {str(ex)}")
