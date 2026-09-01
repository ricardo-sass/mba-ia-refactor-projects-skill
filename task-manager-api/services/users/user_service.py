from __future__ import annotations

import re
from typing import Any

from models.users import User
from models.users.user import VALID_ROLES
from shared.errors import AppError


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$")
MIN_PASSWORD_LENGTH = 8


class UserService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def list_users(self) -> list[dict]:
        result = []
        for user in self.repository.list_with_tasks():
            data = user.to_dict()
            data["task_count"] = len(user.tasks)
            result.append(data)
        return result

    def get_user(self, user_id: int) -> dict:
        user = self._required_user(user_id, with_tasks=True)
        data = user.to_dict()
        data["tasks"] = [task.to_dict() for task in user.tasks]
        return data

    def create_user(self, data: Any) -> dict:
        if not isinstance(data, dict) or not data:
            raise AppError("Dados inválidos", 400)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not isinstance(name, str) or not name:
            raise AppError("Nome é obrigatório", 400)
        if not email:
            raise AppError("Email é obrigatório", 400)
        if not password:
            raise AppError("Senha é obrigatória", 400)
        self._validate_email(email)
        self._validate_password(
            password,
            f"Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres",
        )
        if self.repository.find_by_email(email):
            raise AppError("Email já cadastrado", 409)
        self._validate_role(role)

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        self.repository.add(user)
        self.repository.commit()
        return user.to_dict()

    def update_user(self, user_id: int, data: Any, actor) -> dict:
        user = self._required_user(user_id)
        if actor.role != "admin" and actor.id != user_id:
            raise AppError("Acesso negado", 403)
        if not isinstance(data, dict) or not data:
            raise AppError("Dados inválidos", 400)

        if "name" in data:
            if not isinstance(data["name"], str) or not data["name"]:
                raise AppError("Nome é obrigatório", 400)
            user.name = data["name"]
        if "email" in data:
            self._validate_email(data["email"])
            existing = self.repository.find_by_email(data["email"])
            if existing and existing.id != user_id:
                raise AppError("Email já cadastrado", 409)
            user.email = data["email"]
        if "password" in data:
            self._validate_password(data["password"], "Senha muito curta")
            user.set_password(data["password"])
        if "role" in data:
            if actor.role != "admin":
                raise AppError("Acesso negado", 403)
            self._validate_role(data["role"])
            user.role = data["role"]
        if "active" in data:
            if not isinstance(data["active"], bool):
                raise AppError("Dados inválidos", 400)
            user.active = data["active"]

        self.repository.commit()
        return user.to_dict()

    def delete_user(self, user_id: int) -> dict:
        user = self._required_user(user_id)
        self.repository.delete_user_and_tasks(user)
        self.repository.commit()
        return {"message": "Usuário deletado com sucesso"}

    def user_tasks(self, user_id: int) -> list[dict]:
        self._required_user(user_id)
        result = []
        for task in self.repository.tasks_for_user(user_id):
            result.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": str(task.created_at),
                    "due_date": str(task.due_date) if task.due_date else None,
                    "overdue": task.is_overdue(),
                }
            )
        return result

    def _required_user(self, user_id: int, *, with_tasks: bool = False) -> User:
        user = self.repository.find_by_id(user_id, with_tasks=with_tasks)
        if not user:
            raise AppError("Usuário não encontrado", 404)
        return user

    @staticmethod
    def _validate_email(email: Any) -> None:
        if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email):
            raise AppError("Email inválido", 400)

    @staticmethod
    def _validate_password(password: Any, message: str) -> None:
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise AppError(message, 400)

    @staticmethod
    def _validate_role(role: Any) -> None:
        if role not in VALID_ROLES:
            raise AppError("Role inválido", 400)
