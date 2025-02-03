from fastapi import FastAPI
import uvicorn
from src.routers import deep_seek_router


def create_app() -> FastAPI: 
     app = FastAPI(title="Deep Seek API", description="Application Interface Connecting to Deep-Seek-1 LLM")

     app.include_router(deep_seek_router.router)
     return app

def main(): 
     app = create_app()
     uvicorn.run("main:create_app", host="127.0.0.1", reload=True)
     
if __name__ == "__main__": 
     main()
    