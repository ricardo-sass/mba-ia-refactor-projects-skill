from __future__ import annotations

from sqlalchemy import case, func, select

from models.categories import Category
from models.tasks import Task
from models.users import User


class ReportRepository:
    def __init__(self, session) -> None:
        self.session = session

    def entity_totals(self) -> dict[str, int]:
        return {
            "total_tasks": self.session.scalar(select(func.count(Task.id))) or 0,
            "total_users": self.session.scalar(select(func.count(User.id))) or 0,
            "total_categories": self.session.scalar(select(func.count(Category.id))) or 0,
        }

    def task_counts_by_status(self) -> dict[str, int]:
        rows = self.session.execute(
            select(Task.status, func.count(Task.id)).group_by(Task.status)
        ).all()
        return {status: count for status, count in rows}

    def task_counts_by_priority(self) -> dict[int, int]:
        rows = self.session.execute(
            select(Task.priority, func.count(Task.id)).group_by(Task.priority)
        ).all()
        return {priority: count for priority, count in rows}

    def overdue_tasks(self, now) -> list[Task]:
        statement = select(Task).where(
            Task.due_date.is_not(None),
            Task.due_date < now,
            Task.status.not_in(("done", "cancelled")),
        )
        return list(self.session.execute(statement).scalars().all())

    def recent_counts(self, since) -> tuple[int, int]:
        created = self.session.scalar(
            select(func.count(Task.id)).where(Task.created_at >= since)
        ) or 0
        completed = self.session.scalar(
            select(func.count(Task.id)).where(
                Task.status == "done",
                Task.updated_at >= since,
            )
        ) or 0
        return created, completed

    def user_productivity(self) -> list[tuple[int, str, int, int]]:
        completed = func.sum(case((Task.status == "done", 1), else_=0))
        statement = (
            select(User.id, User.name, func.count(Task.id), completed)
            .outerjoin(Task, Task.user_id == User.id)
            .group_by(User.id, User.name)
        )
        return [
            (user_id, name, total, int(done or 0))
            for user_id, name, total, done in self.session.execute(statement)
        ]

    def find_user(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def tasks_for_user(self, user_id: int) -> list[Task]:
        return list(
            self.session.execute(select(Task).where(Task.user_id == user_id))
            .scalars()
            .all()
        )
