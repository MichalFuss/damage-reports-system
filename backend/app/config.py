"""Shared paths / constants for the running app."""

from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent

FRONTEND_DIR = PROJECT_DIR / "frontend"

# Generated re-occupation PDFs live here and are served statically.
PDF_DIR = BACKEND_DIR / "generated-pdfs"
PDF_URL_PREFIX = "/generated-pdfs"
