from __future__ import annotations

import re
from typing import Any

from models.categories import Category
from shared.errors import AppError


class CategoryController:
    def __init__(self, repository) -> None:
        self.repository = repository

    def list(self) -> list[dict]:
        result = []
        for category, task_count in self.repository.list_with_task_count():
            data = category.to_dict()
            data["task_count"] = task_count
            result.append(data)
        return result

    def create(self, data: Any) -> dict:
        payload = self._required_payload(data)
        name = payload.get("name")
        if not isinstance(name, str) or not name:
            raise AppError("Nome é obrigatório", 400)
        self._validate_optional_fields(payload)
        category = Category(
            name=name,
            description=payload.get("description", ""),
            color=payload.get("color", "#000000"),
        )
        self.repository.add(category)
        self.repository.commit()
        return category.to_dict()

    def update(self, category_id: int, data: Any) -> dict:
        category = self._required_category(category_id)
        payload = self._required_payload(data)
        self._validate_optional_fields(payload)
        if "name" in payload and (
            not isinstance(payload["name"], str) or not payload["name"]
        ):
            raise AppError("Nome é obrigatório", 400)
        for field in ("name", "description", "color"):
            if field in payload:
                setattr(category, field, payload[field])
        self.repository.commit()
        return category.to_dict()

    def delete(self, category_id: int) -> dict:
        category = self._required_category(category_id)
        self.repository.delete(category)
        self.repository.commit()
        return {"message": "Categoria deletada"}

    def _required_category(self, category_id: int) -> Category:
        category = self.repository.find_by_id(category_id)
        if not category:
            raise AppError("Categoria não encontrada", 404)
        return category

    @staticmethod
    def _required_payload(data: Any) -> dict:
        if not isinstance(data, dict) or not data:
            raise AppError("Dados inválidos", 400)
        return data

    @staticmethod
    def _validate_optional_fields(data: dict) -> None:
        if "description" in data and not isinstance(data["description"], str):
            raise AppError("Dados inválidos", 400)
        if "color" in data:
            color = data["color"]
            if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
                raise AppError("Cor inválida", 400)
