"""Script para popular o banco com dados iniciais."""

from datetime import timedelta

from sqlalchemy import delete, func, select

from app import app
from models.categories import Category
from models.tasks import Task
from models.users import User
from shared.database import db
from shared.time import utc_now


def seed_data() -> None:
    with app.app_context():
        db.create_all()
        try:
            db.session.execute(delete(Task))
            db.session.execute(delete(User))
            db.session.execute(delete(Category))

            users = [
                User(name="João Silva", email="joao@email.com", role="admin"),
                User(name="Maria Santos", email="maria@email.com", role="user"),
                User(name="Pedro Oliveira", email="pedro@email.com", role="manager"),
            ]
            for user, password in zip(users, ("1234", "abcd", "pass"), strict=True):
                user.set_password(password)
            db.session.add_all(users)

            categories = [
                Category(name="Backend", description="Tarefas de backend", color="#3498db"),
                Category(name="Frontend", description="Tarefas de frontend", color="#2ecc71"),
                Category(name="DevOps", description="Tarefas de infraestrutura", color="#e74c3c"),
                Category(name="Bug", description="Correção de bugs", color="#e67e22"),
            ]
            db.session.add_all(categories)
            db.session.flush()

            now = utc_now()
            tasks_data = [
                {"title": "Implementar autenticação JWT", "description": "Adicionar autenticação real com JWT", "status": "pending", "priority": 1, "user_id": users[0].id, "category_id": categories[0].id, "due_date": now - timedelta(days=3)},
                {"title": "Criar tela de login", "description": "Tela de login responsiva", "status": "in_progress", "priority": 2, "user_id": users[1].id, "category_id": categories[1].id, "due_date": now + timedelta(days=5)},
                {"title": "Configurar CI/CD", "description": "Pipeline com GitHub Actions", "status": "done", "priority": 2, "user_id": users[2].id, "category_id": categories[2].id, "tags": "devops,ci,github"},
                {"title": "Corrigir bug no filtro de busca", "description": "Filtro não funciona com caracteres especiais", "status": "pending", "priority": 1, "user_id": users[0].id, "category_id": categories[3].id, "due_date": now - timedelta(days=1)},
                {"title": "Adicionar paginação na API", "description": "Endpoints retornam todos os registros", "status": "pending", "priority": 3, "user_id": users[0].id, "category_id": categories[0].id, "due_date": now + timedelta(days=10)},
                {"title": "Escrever testes unitários", "description": "Cobertura mínima de 80%", "status": "pending", "priority": 2, "user_id": users[1].id, "category_id": categories[0].id},
                {"title": "Documentar API com Swagger", "description": "Gerar documentação automática", "status": "cancelled", "priority": 4, "user_id": users[2].id, "category_id": categories[0].id},
                {"title": "Refatorar models", "description": "Melhorar organização dos models", "status": "in_progress", "priority": 3, "user_id": users[1].id, "category_id": categories[0].id, "tags": "refactor,tech-debt"},
                {"title": "Configurar monitoramento", "description": "Prometheus + Grafana", "status": "pending", "priority": 4, "user_id": users[2].id, "category_id": categories[2].id, "due_date": now + timedelta(days=20)},
                {"title": "Melhorar validações de input", "description": "Usar marshmallow ou pydantic", "status": "pending", "priority": 3, "user_id": users[0].id, "category_id": categories[0].id, "tags": "improvement,validation"},
            ]
            db.session.add_all([Task(**data) for data in tasks_data])
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        print("Seed concluído com sucesso!")
        print(f"  {db.session.scalar(select(func.count(User.id)))} usuários")
        print(f"  {db.session.scalar(select(func.count(Category.id)))} categorias")
        print(f"  {db.session.scalar(select(func.count(Task.id)))} tasks")


if __name__ == "__main__":
    seed_data()
