from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from models.categories import Category
from models.tasks import Task
from models.users import User


class TaskRepository:
    def __init__(self, session) -> None:
        self.session = session

    def list_enriched(self) -> list[Task]:
        statement = select(Task).options(
            selectinload(Task.user),
            selectinload(Task.category),
        )
        return list(self.session.execute(statement).scalars().all())

    def find_by_id(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def find_user(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def find_category(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def search(
        self,
        *,
        query: str = "",
        status: str = "",
        priority: int | None = None,
        user_id: int | None = None,
    ) -> list[Task]:
        statement = select(Task)
        if query:
            statement = statement.where(
                or_(
                    Task.title.like(f"%{query}%"),
                    Task.description.like(f"%{query}%"),
                )
            )
        if status:
            statement = statement.where(Task.status == status)
        if priority is not None:
            statement = statement.where(Task.priority == priority)
        if user_id is not None:
            statement = statement.where(Task.user_id == user_id)
        return list(self.session.execute(statement).scalars().all())

    def counts_by_status(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Task.status, func.count(Task.id)).group_by(Task.status)
        ).all()
        return {status: count for status, count in rows}

    def all_for_statistics(self) -> list[Task]:
        return list(self.session.execute(select(Task)).scalars().all())

    def add(self, task: Task) -> None:
        self.session.add(task)

    def delete(self, task: Task) -> None:
        self.session.delete(task)

    def commit(self) -> None:
        self.session.commit()
