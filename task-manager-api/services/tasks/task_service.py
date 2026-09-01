from __future__ import annotations

from datetime import datetime
from typing import Any

from models.tasks import Task
from models.tasks.task import MAX_PRIORITY, MIN_PRIORITY, VALID_STATUSES
from shared.errors import AppError
from shared.time import utc_now


class TaskService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def list_tasks(self) -> list[dict]:
        result = []
        for task in self.repository.list_enriched():
            data = task.to_dict()
            data["overdue"] = task.is_overdue()
            data["user_name"] = task.user.name if task.user else None
            data["category_name"] = task.category.name if task.category else None
            result.append(data)
        return result

    def get_task(self, task_id: int) -> dict:
        task = self._required_task(task_id)
        data = task.to_dict()
        data["overdue"] = task.is_overdue()
        return data

    def create_task(self, data: Any) -> dict:
        payload = self._validate_payload(data, creating=True)
        task = Task(**payload)
        self.repository.add(task)
        self.repository.commit()
        return task.to_dict()

    def update_task(self, task_id: int, data: Any) -> dict:
        task = self._required_task(task_id)
        payload = self._validate_payload(data, creating=False)
        for field, value in payload.items():
            setattr(task, field, value)
        task.updated_at = utc_now()
        self.repository.commit()
        return task.to_dict()

    def delete_task(self, task_id: int) -> dict:
        task = self._required_task(task_id)
        self.repository.delete(task)
        self.repository.commit()
        return {"message": "Task deletada com sucesso"}

    def search_tasks(self, args: dict[str, str]) -> list[dict]:
        priority = self._optional_query_int(args.get("priority", ""), "Prioridade inválida")
        user_id = self._optional_query_int(args.get("user_id", ""), "Usuário inválido")
        tasks = self.repository.search(
            query=args.get("q", ""),
            status=args.get("status", ""),
            priority=priority,
            user_id=user_id,
        )
        return [task.to_dict() for task in tasks]

    def statistics(self) -> dict:
        counts = self.repository.counts_by_status()
        total = sum(counts.values())
        done = counts.get("done", 0)
        overdue = sum(task.is_overdue() for task in self.repository.all_for_statistics())
        return {
            "total": total,
            "pending": counts.get("pending", 0),
            "in_progress": counts.get("in_progress", 0),
            "done": done,
            "cancelled": counts.get("cancelled", 0),
            "overdue": overdue,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        }

    def _required_task(self, task_id: int) -> Task:
        task = self.repository.find_by_id(task_id)
        if not task:
            raise AppError("Task não encontrada", 404)
        return task

    def _validate_payload(self, data: Any, *, creating: bool) -> dict:
        if not isinstance(data, dict) or not data:
            raise AppError("Dados inválidos", 400)

        payload: dict[str, Any] = {}
        if creating or "title" in data:
            title = data.get("title")
            if not title:
                raise AppError("Título é obrigatório" if creating else "Título muito curto", 400)
            if not isinstance(title, str):
                raise AppError("Dados inválidos", 400)
            if len(title) < 3:
                raise AppError("Título muito curto", 400)
            if len(title) > 200:
                raise AppError("Título muito longo", 400)
            payload["title"] = title

        if creating or "description" in data:
            description = data.get("description", "")
            if description is not None and not isinstance(description, str):
                raise AppError("Dados inválidos", 400)
            payload["description"] = description

        if creating or "status" in data:
            status = data.get("status", "pending")
            if status not in VALID_STATUSES:
                raise AppError("Status inválido", 400)
            payload["status"] = status

        if creating or "priority" in data:
            priority = data.get("priority", 3)
            if not isinstance(priority, int) or isinstance(priority, bool):
                raise AppError("Prioridade deve ser entre 1 e 5", 400)
            if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
                raise AppError("Prioridade deve ser entre 1 e 5", 400)
            payload["priority"] = priority

        for field, finder, message in (
            ("user_id", self.repository.find_user, "Usuário não encontrado"),
            ("category_id", self.repository.find_category, "Categoria não encontrada"),
        ):
            if creating or field in data:
                value = data.get(field)
                if value is not None and (
                    not isinstance(value, int) or isinstance(value, bool)
                ):
                    raise AppError("Dados inválidos", 400)
                if value is not None and not finder(value):
                    raise AppError(message, 404)
                payload[field] = value

        if creating or "due_date" in data:
            due_date = data.get("due_date")
            if due_date:
                if not isinstance(due_date, str):
                    raise AppError("Formato de data inválido", 400)
                try:
                    payload["due_date"] = datetime.strptime(due_date, "%Y-%m-%d")
                except (TypeError, ValueError):
                    message = "Formato de data inválido. Use YYYY-MM-DD" if creating else "Formato de data inválido"
                    raise AppError(message, 400)
            else:
                payload["due_date"] = None

        if creating or "tags" in data:
            tags = data.get("tags")
            if isinstance(tags, list):
                if not all(isinstance(tag, str) for tag in tags):
                    raise AppError("Dados inválidos", 400)
                payload["tags"] = ",".join(tags)
            elif tags is None or isinstance(tags, str):
                payload["tags"] = tags
            else:
                raise AppError("Dados inválidos", 400)
        return payload

    @staticmethod
    def _optional_query_int(value: str, message: str) -> int | None:
        if value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise AppError(message, 400)
