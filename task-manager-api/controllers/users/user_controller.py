from __future__ import annotations

from typing import Any

from shared.errors import AppError


class UserController:
    def __init__(self, service, auth_service) -> None:
        self.service = service
        self.auth_service = auth_service

    def list(self) -> list[dict]:
        return self.service.list_users()

    def get(self, user_id: int) -> dict:
        return self.service.get_user(user_id)

    def create(self, data: Any) -> dict:
        return self.service.create_user(data)

    def update(self, user_id: int, data: Any, actor) -> dict:
        return self.service.update_user(user_id, data, actor)

    def delete(self, user_id: int) -> dict:
        return self.service.delete_user(user_id)

    def tasks(self, user_id: int) -> list[dict]:
        return self.service.user_tasks(user_id)

    def login(self, data: Any) -> dict:
        if not isinstance(data, dict) or not data:
            raise AppError("Dados inválidos", 400)
        user, token = self.auth_service.login(data.get("email"), data.get("password"))
        return {
            "message": "Login realizado com sucesso",
            "user": user,
            "token": token,
        }
