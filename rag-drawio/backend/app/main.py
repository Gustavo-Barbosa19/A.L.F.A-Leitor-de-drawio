import os
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .api.routes import router, embedding_service, vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    vector_size = embedding_service.get_dimension()
    try:
        vector_store._ensure_collection(vector_size=vector_size)
    except Exception as e:
        print(f"Warning: Qdrant pode nao estar disponivel: {e}")
    yield


app = FastAPI(
    title="IA RAG - Leitor de Draw.io",
    description="Sistema de IA RAG especializado em leitura de arquivos DRAW.IO (.drawio)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "IA RAG - Leitor de Draw.io", "status": "online", "docs": "/docs"}


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
