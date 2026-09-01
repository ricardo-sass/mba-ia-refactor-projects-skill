import hashlib
import unittest
from datetime import datetime, timedelta

from models.tasks import Task
from models.users import User
from services.users import AuthService
from shared.errors import AppError


class FakeUserRepository:
    def __init__(self, user):
        self.user = user
        self.commits = 0

    def find_by_email(self, email):
        return self.user if self.user.email == email else None

    def find_by_id(self, user_id, *, with_tasks=False):
        return self.user if self.user.id == user_id else None

    def commit(self):
        self.commits += 1


class ModelAndAuthTests(unittest.TestCase):
    def test_hash_de_senha_e_adaptativo_e_salgado(self):
        first = User(name="A", email="a@example.com")
        second = User(name="B", email="b@example.com")

        first.set_password("segredo")
        second.set_password("segredo")

        self.assertNotEqual(first.password, second.password)
        self.assertFalse(first.has_legacy_password)
        self.assertTrue(first.check_password("segredo"))
        self.assertFalse(first.check_password("incorreto"))

    def test_serializer_publico_nao_expoe_senha(self):
        user = User(name="A", email="a@example.com", role="user", active=True)
        user.password = "valor-interno"
        self.assertNotIn("password", user.to_dict())

    def test_login_migra_hash_md5_legado(self):
        user = User(id=7, name="A", email="a@example.com", role="user", active=True)
        user.password = hashlib.md5(b"segredo").hexdigest()
        repository = FakeUserRepository(user)
        service = AuthService(repository, "segredo-de-teste")

        payload, token = service.login("a@example.com", "segredo")

        self.assertEqual(payload["id"], 7)
        self.assertTrue(token)
        self.assertFalse(user.has_legacy_password)
        self.assertEqual(repository.commits, 1)

    def test_token_forjado_e_rejeitado(self):
        user = User(id=7, name="A", email="a@example.com", role="user", active=True)
        user.set_password("segredo")
        service = AuthService(FakeUserRepository(user), "segredo-de-teste")

        with self.assertRaises(AppError) as context:
            service.verify_token("token-forjado")

        self.assertEqual(context.exception.status, 401)

    def test_regra_de_atraso_tem_relogio_deterministico(self):
        reference = datetime(2030, 1, 10, 12, 0, 0)
        task = Task(due_date=reference - timedelta(days=1), status="pending")
        self.assertTrue(task.is_overdue(reference))
        task.status = "done"
        self.assertFalse(task.is_overdue(reference))


if __name__ == "__main__":
    unittest.main()
