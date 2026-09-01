from datetime import UTC, datetime


def utc_now() -> datetime:
    """Retorna UTC sem tzinfo para compatibilidade com os registros SQLite existentes."""

    return datetime.now(UTC).replace(tzinfo=None)
