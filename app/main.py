from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from rich.console import Console

from app.api.v1.endpoints.crop import router as crop_router
from app.db.session import engine
from app.db.models import Base

console = Console()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="QOVES Frontal Crop API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(crop_router, prefix="/api/v1/frontal/crop", tags=["Crop"])

console.log("[bold green]🚀 QOVES Frontal Crop API is running![/bold green]")
