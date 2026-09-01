from datetime import timedelta

from shared.errors import AppError
from shared.time import utc_now


class ReportService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def summary(self) -> dict:
        now = utc_now()
        seven_days_ago = now - timedelta(days=7)
        overview = self.repository.entity_totals()
        statuses = self.repository.task_counts_by_status()
        priorities = self.repository.task_counts_by_priority()
        overdue_tasks = self.repository.overdue_tasks(now)
        recent_created, recent_done = self.repository.recent_counts(seven_days_ago)

        overdue_list = [
            {
                "id": task.id,
                "title": task.title,
                "due_date": str(task.due_date),
                "days_overdue": (now - task.due_date).days,
            }
            for task in overdue_tasks
        ]
        productivity = []
        for user_id, user_name, total, completed in self.repository.user_productivity():
            productivity.append(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": round((completed / total) * 100, 2) if total else 0,
                }
            )

        return {
            "generated_at": str(now),
            "overview": overview,
            "tasks_by_status": {
                "pending": statuses.get("pending", 0),
                "in_progress": statuses.get("in_progress", 0),
                "done": statuses.get("done", 0),
                "cancelled": statuses.get("cancelled", 0),
            },
            "tasks_by_priority": {
                "critical": priorities.get(1, 0),
                "high": priorities.get(2, 0),
                "medium": priorities.get(3, 0),
                "low": priorities.get(4, 0),
                "minimal": priorities.get(5, 0),
            },
            "overdue": {"count": len(overdue_list), "tasks": overdue_list},
            "recent_activity": {
                "tasks_created_last_7_days": recent_created,
                "tasks_completed_last_7_days": recent_done,
            },
            "user_productivity": productivity,
        }

    def user_report(self, user_id: int) -> dict:
        user = self.repository.find_user(user_id)
        if not user:
            raise AppError("Usuário não encontrado", 404)
        tasks = self.repository.tasks_for_user(user_id)
        counts = {status: 0 for status in ("done", "pending", "in_progress", "cancelled")}
        for task in tasks:
            if task.status in counts:
                counts[task.status] += 1
        total = len(tasks)
        done = counts["done"]
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": {
                "total_tasks": total,
                **counts,
                "overdue": sum(task.is_overdue() for task in tasks),
                "high_priority": sum(task.priority <= 2 for task in tasks),
                "completion_rate": round((done / total) * 100, 2) if total else 0,
            },
        }
