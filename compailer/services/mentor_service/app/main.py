from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from services.mentor_service import router as mentor_router

app = FastAPI(title="Mentor Service", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mentor_router)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "mentor"}
