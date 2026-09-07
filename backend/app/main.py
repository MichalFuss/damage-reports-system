"""
FastAPI entry point.

Mounts the routers, serves generated PDFs and the static frontend, and seeds
the in-memory store on startup.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import repository
from .config import FRONTEND_DIR, PDF_DIR, PDF_URL_PREFIX
from .routers import buildings, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    repository.seed()
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="מערכת ניהול דיווחי נזק", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(reports.router)
app.include_router(buildings.router)

PDF_DIR.mkdir(parents=True, exist_ok=True)
app.mount(PDF_URL_PREFIX, StaticFiles(directory=PDF_DIR), name="generated-pdfs")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
