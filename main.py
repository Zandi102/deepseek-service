from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn 
from src.routers import deep_seek_router


def create_app() -> FastAPI: 
     app = FastAPI(title="Deep Seek API", description="Application Interface Connecting to Deep-Seek-1 LLM")
     # Enable CORS for all origins (allow frontend to communicate)
     app.add_middleware(
          CORSMiddleware,
          allow_origins=["*"],  
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
    )

     app.include_router(deep_seek_router.router)
     return app

def main(): 
     app = create_app()
     uvicorn.run("main:create_app", host="127.0.0.1", reload=True)
     
if __name__ == "__main__": 
     main()
    