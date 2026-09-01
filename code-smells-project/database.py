"""Compatibilidade para consumidores antigos da conexão de banco."""

import os

from shared.database import close_db, get_db, init_app, initialize_database


db_connection = None
db_path = os.getenv("DATABASE_PATH", "loja.db")


__all__ = ["close_db", "get_db", "init_app", "initialize_database"]
