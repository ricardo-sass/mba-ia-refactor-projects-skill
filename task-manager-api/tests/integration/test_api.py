import unittest

from sqlalchemy import event

from app import create_app
from models.categories import Category
from models.tasks import Task
from models.users import User
from shared.database import db


class ApiIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "SECRET_KEY": "segredo-exclusivo-de-teste",
                "TOKEN_MAX_AGE": 3600,
            }
        )
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()

        admin = User(name="Admin", email="admin@example.com", role="admin")
        admin.set_password("segredo")
        category = Category(name="Teste", description="Integração", color="#123456")
        db.session.add_all([admin, category])
        db.session.flush()
        db.session.add_all(
            [
                Task(
                    title=f"Task {index}",
                    description="Teste",
                    user_id=admin.id,
                    category_id=category.id,
                )
                for index in range(5)
            ]
        )
        db.session.commit()
        self.admin = admin
        self.client = self.app.test_client()
        login = self.client.post(
            "/login",
            json={"email": "admin@example.com", "password": "segredo"},
        )
        self.token = login.get_json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_usuario_e_login_nao_expoem_hash(self):
        login = self.client.post(
            "/login",
            json={"email": "admin@example.com", "password": "segredo"},
        )
        detail = self.client.get(f"/users/{self.admin.id}", headers=self.headers)

        self.assertNotIn("password", login.get_json()["user"])
        self.assertNotIn("password", detail.get_json())

    def test_mutacao_exige_token_valido(self):
        anonymous = self.client.post("/tasks", json={"title": "Anônima"})
        forged = self.client.post(
            "/tasks",
            json={"title": "Forjada"},
            headers={"Authorization": "Bearer token-forjado"},
        )
        valid = self.client.post(
            "/tasks",
            json={"title": "Autorizada"},
            headers=self.headers,
        )

        self.assertEqual(anonymous.status_code, 401)
        self.assertEqual(forged.status_code, 401)
        self.assertEqual(valid.status_code, 201)

    def test_entrada_invalida_retorna_json_400(self):
        invalid_body = self.client.post("/tasks", json=["inválido"], headers=self.headers)
        invalid_query = self.client.get(
            "/tasks/search?priority=abc",
            headers=self.headers,
        )

        self.assertEqual(invalid_body.status_code, 400)
        self.assertTrue(invalid_body.is_json)
        self.assertEqual(invalid_query.status_code, 400)
        self.assertTrue(invalid_query.is_json)

    def test_nova_senha_exige_oito_caracteres(self):
        response = self.client.post(
            "/users",
            json={
                "name": "Senha Curta",
                "email": "curta@example.com",
                "password": "1234",
            },
            headers=self.headers,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Senha deve ter no mínimo 8 caracteres",
        )

    def test_listagem_de_tasks_nao_cresce_em_n_mais_um(self):
        statements = []

        def count_queries(connection, cursor, statement, parameters, context, executemany):
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(statement)

        event.listen(db.engine, "before_cursor_execute", count_queries)
        try:
            response = self.client.get("/tasks", headers=self.headers)
        finally:
            event.remove(db.engine, "before_cursor_execute", count_queries)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 5)
        self.assertLessEqual(len(statements), 4)


if __name__ == "__main__":
    unittest.main()
