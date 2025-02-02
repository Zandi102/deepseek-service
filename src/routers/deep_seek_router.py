
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

    async def listen(self, max_attempts=3, timeout=10):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source)
            attempts = 0
            while attempts < max_attempts:
                try:
                    audio = recognizer.listen(source, timeout=30)
                    text = recognizer.recognize_google(audio)
                    print("You said:", text)
                    return text
                except sr.UnknownValueError:
                    print("Could not understand the audio, retrying...")
                    await self.speak("Sorry, I couldn't understand that, please repeat.")
                except sr.RequestError:
                    print("Speech recognition service is unavailable, retrying...")
                    await self.speak("Sorry, the speech recognition service is unavailable.")
                except Exception as e:
                    print(f"Error during listening: {str(e)}")
                    await self.speak("Sorry, there was an error, please try again.")
                
                attempts += 1
            
            # If no valid input after max_attempts, return default message
            return "Sorry, I couldn't catch that after several attempts."

    @router.get('/nova')
    async def begin_ai_integration(self):    
        while True:
            try:
                user_input = await self.listen()

                for command in ["Nova exit", "Nova quit", "Nova stop"]:
                    if command in user_input:
                        await self.speak("Goodbye Alex!")
                        return
                            
            except Exception as ex:
                raise Exception(f'Error listening to user to to exception {str(ex)}')
            
            try:
                response_object = ollama.chat(
                    model=self.model_version,
                    messages=[{'role': 'user', 'content': user_input}],
                    options={'num_predict': 100}  # Adjust to control response length
                )
                
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
                
                ollama_response = OllamaResponse(thought_process=ai_thoughts, 
                                                    response=ai_response)

                await self.speak(ollama_response.response)
                                    
            except Exception as ex:
                raise ex
