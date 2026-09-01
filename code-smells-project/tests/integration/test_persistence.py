import os
import sqlite3
import tempfile
import unittest

from app import create_app
from models.usuarios import UserModel
from repositories.pedidos import OrderRepository
from services.usuarios import UserService
from shared.database import get_db


class PersistenceIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="code-smells-integration-")
        self.db_path = os.path.join(self.temp_dir.name, "loja.db")
        self.application = create_app(
            {
                "TESTING": True,
                "APP_ENV": "test",
                "DATABASE_PATH": self.db_path,
                "SECRET_KEY": "segredo-da-integracao",
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_connection_is_closed_at_end_of_application_context(self):
        with self.application.app_context():
            connection = get_db()
            connection.execute("SELECT 1")

        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")

    def test_order_rolls_back_all_writes_when_second_item_fails(self):
        with self.application.app_context():
            connection = get_db()
            original_stock = {
                row["id"]: row["estoque"]
                for row in connection.execute("SELECT id, estoque FROM produtos WHERE id IN (1, 2)")
            }
            connection.executescript(
                """
                CREATE TRIGGER falhar_segundo_item
                BEFORE INSERT ON itens_pedido
                WHEN NEW.produto_id = 2
                BEGIN
                    SELECT RAISE(ABORT, 'falha controlada');
                END;
                """
            )
            connection.commit()

            repository = OrderRepository(get_db)
            with self.assertRaises(sqlite3.IntegrityError):
                repository.create(
                    1,
                    [
                        {"produto_id": 1, "quantidade": 1},
                        {"produto_id": 2, "quantidade": 1},
                    ],
                )

            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0])
            self.assertEqual(0, connection.execute("SELECT COUNT(*) FROM itens_pedido").fetchone()[0])
            current_stock = {
                row["id"]: row["estoque"]
                for row in connection.execute("SELECT id, estoque FROM produtos WHERE id IN (1, 2)")
            }
            self.assertEqual(original_stock, current_stock)

    def test_order_listing_uses_one_select(self):
        with self.application.app_context():
            connection = get_db()
            repository = OrderRepository(get_db)
            repository.create(1, [{"produto_id": 1, "quantidade": 1}])
            repository.create(1, [{"produto_id": 2, "quantidade": 1}])

            statements = []
            connection.set_trace_callback(statements.append)
            orders = repository.list_all()
            connection.set_trace_callback(None)

            selects = [statement for statement in statements if statement.lstrip().upper().startswith("SELECT")]
            self.assertEqual(2, len(orders))
            self.assertEqual(1, len(selects), selects)

    def test_legacy_plaintext_password_is_migrated_after_valid_login(self):
        with self.application.app_context():
            connection = get_db()
            cursor = connection.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                ("Legado", "legado@example.com", "senha-legada", "cliente"),
            )
            connection.commit()
            user_id = cursor.lastrowid

            user_model = UserModel(get_db)
            authenticated = UserService(user_model).authenticate("legado@example.com", "senha-legada")
            stored = connection.execute("SELECT senha FROM usuarios WHERE id = ?", (user_id,)).fetchone()[0]

            self.assertEqual(user_id, authenticated["id"])
            self.assertNotEqual("senha-legada", stored)
            self.assertTrue(stored.startswith(("scrypt:", "pbkdf2:", "argon2:")))


if __name__ == "__main__":
    unittest.main()
