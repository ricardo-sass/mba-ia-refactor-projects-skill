from flask import jsonify
from werkzeug.exceptions import HTTPException


class DomainError(Exception):
    status_code = 400

    def __init__(self, message):
        super().__init__(message)
        self.public_message = message


class ValidationError(DomainError):
    status_code = 400


class AuthenticationError(DomainError):
    status_code = 401


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        return jsonify({"erro": error.public_message, "sucesso": False}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description, "sucesso": False}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Falha não tratada durante a requisição")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

