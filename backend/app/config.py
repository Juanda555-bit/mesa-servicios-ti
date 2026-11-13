"""Configuración leída del archivo .env (ver .env.example)."""

import os
import secrets
import warnings

from dotenv import load_dotenv

from db.database import BACKEND_DIR

load_dotenv(BACKEND_DIR.parent / ".env")

SECRET_KEY = os.getenv("SECRET_KEY") or ""
if not SECRET_KEY:
    # Sin clave en .env se genera una temporal: la app funciona, pero los tokens
    # dejan de valer cada vez que se reinicia el servidor.
    SECRET_KEY = secrets.token_urlsafe(32)
    warnings.warn("SECRET_KEY no está definida en .env; se usa una clave temporal.", stacklevel=2)

ALGORITMO_JWT = "HS256"
TOKEN_MINUTOS = int(os.getenv("TOKEN_MINUTOS", "480"))

CORS_ORIGINS = [
    origen.strip()
    for origen in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origen.strip()
]
