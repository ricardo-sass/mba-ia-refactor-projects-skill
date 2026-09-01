from __future__ import annotations

from typing import Any


class TaskController:
    def __init__(self, service) -> None:
        self.service = service

    def list(self) -> list[dict]:
        return self.service.list_tasks()

    def get(self, task_id: int) -> dict:
        return self.service.get_task(task_id)

    def create(self, data: Any) -> dict:
        return self.service.create_task(data)

    def update(self, task_id: int, data: Any) -> dict:
        return self.service.update_task(task_id, data)

    def delete(self, task_id: int) -> dict:
        return self.service.delete_task(task_id)

    def search(self, args: dict[str, str]) -> list[dict]:
        return self.service.search_tasks(args)

    def statistics(self) -> dict:
        return self.service.statistics()
