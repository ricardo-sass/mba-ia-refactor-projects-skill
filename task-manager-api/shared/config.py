from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def load_config() -> dict:
    load_dotenv()
    return {
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", "sqlite:///tasks.db"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": os.getenv("SECRET_KEY") or secrets.token_urlsafe(48),
        "TOKEN_MAX_AGE": int(os.getenv("TOKEN_MAX_AGE", "3600")),
        "DEBUG": _as_bool(os.getenv("FLASK_DEBUG")),
        "APP_HOST": os.getenv("APP_HOST", "0.0.0.0"),
        "APP_PORT": int(os.getenv("APP_PORT", "5000")),
    }
