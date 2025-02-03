
import asyncio
from fastapi import APIRouter
from fastapi_utils.cbv import cbv
from src.entities.ollama_response import OllamaResponse
from src.entities.deep_seek_request import DeepSeekRequest
import ollama
import re
import speech_recognition as sr
import pyttsx3
import pygame
import edge_tts

router = APIRouter()

@cbv(router)
class DeepSeekRouter:
    def __init__(self):
        self.model_version = "deepseek-r1:1.5b"        
        
    # TODO Microsoft version
    # async def speak(self, text):
    #     # Generate speech and save to a file
    #     communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    #     await communicate.save("output.mp3")
        
    #     await self.play_sound()
    
    # @staticmethod
    # async def play_sound():
    #     pygame.mixer.init()
    #     pygame.mixer.music.load("output.mp3")
    #     pygame.mixer.music.play()
    
        # while pygame.mixer.music.get_busy():
        #     await asyncio.sleep(0.1)
        
    
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
        

    @router.get('/ali')
    async def begin_ai_integration(self):    
        while True:
            try:
                user_input = await self.listen()

                for command in ["Ali exit", "Ali quit", "Ali stop"]:
                    if command.lower() in user_input.lower():
                        await self.speak("Goodbye Alex!")
                        return
                            
            except Exception as ex:
                raise Exception(f'Error listening to user due to exception {str(ex)}')
            
            try:
                response_stream = await asyncio.to_thread(
                    ollama.chat,
                    model=self.model_version,
                    messages=[{'role': 'user', 'content': user_input}],
                    stream=False
                )

                full_response = response_stream.message.content

                print(f"Full AI Response: {full_response}")

                thoughts = re.search(r"<think>(.*?)</think>", full_response, re.DOTALL)
                ai_thoughts = thoughts.group(1).strip().replace('\n', '') if thoughts else ""

                ai_response = re.search(r"</think>\s*(.*)", full_response, re.DOTALL)
                ai_response = ai_response.group(1).strip().replace('\n', '') if ai_response else ""

                ollama_response = OllamaResponse(thought_process=ai_thoughts, response=ai_response)
                
                print(f'Speaking: {ai_response}') 

                await self.speak(ollama_response.response)  
                
            except Exception as ex:
                print(f"Error in AI response: {str(ex)}")
                await self.speak("Sorry, I encountered an issue processing your request.")
