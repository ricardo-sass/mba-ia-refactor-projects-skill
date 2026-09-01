from __future__ import annotations

from dataclasses import dataclass

from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError

from shared.database import db


@dataclass
class AppError(Exception):
    message: str
    status: int = 400

    def __str__(self) -> str:
        return self.message


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": error.message}), error.status

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error: SQLAlchemyError):
        db.session.rollback()
        app.logger.error(
            "Falha de persistência",
            exc_info=(type(error), error, error.__traceback__),
        )
        return jsonify({"error": "Erro interno"}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        db.session.rollback()
        app.logger.error(
            "Falha inesperada",
            exc_info=(type(error), error, error.__traceback__),
        )
        return jsonify({"error": "Erro interno"}), 500
