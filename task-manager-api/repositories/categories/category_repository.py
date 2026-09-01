from __future__ import annotations

from sqlalchemy import func, select

from models.categories import Category
from models.tasks import Task


class CategoryRepository:
    def __init__(self, session) -> None:
        self.session = session

    def list_with_task_count(self) -> list[tuple[Category, int]]:
        statement = (
            select(Category, func.count(Task.id))
            .outerjoin(Task, Task.category_id == Category.id)
            .group_by(Category.id)
        )
        return [(category, count) for category, count in self.session.execute(statement)]

    def find_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def add(self, category: Category) -> None:
        self.session.add(category)

    def delete(self, category: Category) -> None:
        self.session.delete(category)

    def commit(self) -> None:
        self.session.commit()
