from __future__ import annotations

from functools import wraps
from typing import Callable, Iterable

from flask import g, request

from shared.errors import AppError


class AuthMiddleware:
    """Adapta o token do protocolo HTTP para o Service de autenticação."""

    def __init__(self, auth_service) -> None:
        self.auth_service = auth_service

    def required(self, roles: Iterable[str] | None = None) -> Callable:
        accepted_roles = set(roles or ())

        def decorator(view: Callable) -> Callable:
            @wraps(view)
            def wrapped(*args, **kwargs):
                authorization = request.headers.get("Authorization", "")
                if not authorization.startswith("Bearer "):
                    raise AppError("Autenticação obrigatória", 401)
                token = authorization.removeprefix("Bearer ").strip()
                user = self.auth_service.verify_token(token)
                if accepted_roles and user.role not in accepted_roles:
                    raise AppError("Acesso negado", 403)
                g.current_user = user
                return view(*args, **kwargs)

            return wrapped

        return decorator
