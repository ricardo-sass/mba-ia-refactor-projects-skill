import os
import secrets


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "sim", "yes", "on"}


def _cors_origins(value):
    if isinstance(value, (list, tuple)):
        return [str(origin).strip() for origin in value if str(origin).strip()]
    if not value:
        return []
    return [origin.strip() for origin in str(value).split(",") if origin.strip()]


def build_config(overrides=None):
    overrides = dict(overrides or {})
    environment = overrides.get("APP_ENV", os.getenv("APP_ENV", "development"))
    secret_key = overrides.get("SECRET_KEY", os.getenv("SECRET_KEY"))

    if environment == "production" and not secret_key:
        raise RuntimeError("SECRET_KEY é obrigatória no ambiente de produção")
    if not secret_key:
        secret_key = secrets.token_urlsafe(32)

    config = {
        "APP_ENV": environment,
        "DATABASE_PATH": overrides.get("DATABASE_PATH", os.getenv("DATABASE_PATH", "loja.db")),
        "SECRET_KEY": secret_key,
        "DEBUG": _as_bool(overrides.get("DEBUG", os.getenv("DEBUG")), default=False),
        "TESTING": _as_bool(overrides.get("TESTING"), default=False),
        "CORS_ORIGINS": _cors_origins(overrides.get("CORS_ORIGINS", os.getenv("CORS_ORIGINS"))),
    }
    config.update(overrides)
    config["DEBUG"] = _as_bool(config.get("DEBUG"), default=False)
    config["TESTING"] = _as_bool(config.get("TESTING"), default=False)
    config["CORS_ORIGINS"] = _cors_origins(config.get("CORS_ORIGINS"))
    return config
