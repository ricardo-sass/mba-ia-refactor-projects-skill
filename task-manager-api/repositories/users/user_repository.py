from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from models.tasks import Task
from models.users import User


class UserRepository:
    def __init__(self, session) -> None:
        self.session = session

    def list_with_tasks(self) -> list[User]:
        statement = select(User).options(selectinload(User.tasks))
        return list(self.session.execute(statement).scalars().all())

    def find_by_id(self, user_id: int, *, with_tasks: bool = False) -> User | None:
        if not with_tasks:
            return self.session.get(User, user_id)
        statement = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.tasks))
        )
        return self.session.execute(statement).scalar_one_or_none()

    def find_by_email(self, email: str) -> User | None:
        return self.session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def tasks_for_user(self, user_id: int) -> list[Task]:
        return list(
            self.session.execute(select(Task).where(Task.user_id == user_id))
            .scalars()
            .all()
        )

    def delete_user_and_tasks(self, user: User) -> None:
        self.session.execute(delete(Task).where(Task.user_id == user.id))
        self.session.delete(user)

    def add(self, user: User) -> None:
        self.session.add(user)

    def commit(self) -> None:
        self.session.commit()
