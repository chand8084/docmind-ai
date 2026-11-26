
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.question import router as question_router


app = FastAPI(
    title="DocuMind AI",
    description="Universal Document Intelligence Assistant",
    version="1.0.0"
)


# Frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register document upload routes
app.include_router(upload_router)
app.include_router(question_router)

@app.get("/")
def home():
    return {
        "application": "DocuMind AI",
        "message": "Universal Document Intelligence Assistant",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "DocuMind AI Backend"
    }
