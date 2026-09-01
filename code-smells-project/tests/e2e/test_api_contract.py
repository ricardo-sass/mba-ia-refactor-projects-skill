import importlib
import os
import sqlite3
import tempfile
import unittest

from werkzeug.security import check_password_hash


app_module = importlib.import_module("app")
database_module = importlib.import_module("database")


class ApiContractE2ETest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="code-smells-e2e-")
        self.db_path = os.path.join(self.temp_dir.name, "loja.db")
        os.environ["DATABASE_PATH"] = self.db_path
        os.environ["SECRET_KEY"] = "segredo-exclusivo-da-suite-e2e"
        os.environ["APP_ENV"] = "test"
        os.environ["CORS_ORIGINS"] = "https://cliente.exemplo"

        connection = getattr(database_module, "db_connection", None)
        if connection is not None:
            connection.close()
        database_module.db_connection = None
        database_module.db_path = self.db_path

        if hasattr(app_module, "create_app"):
            self.application = app_module.create_app(
                {
                    "TESTING": True,
                    "DATABASE_PATH": self.db_path,
                    "SECRET_KEY": "segredo-exclusivo-da-suite-e2e",
                    "APP_ENV": "test",
                    "CORS_ORIGINS": ["https://cliente.exemplo"],
                }
            )
        else:
            self.application = app_module.app
            self.application.config["TESTING"] = True

        self.client = self.application.test_client()

    def tearDown(self):
        connection = getattr(database_module, "db_connection", None)
        if connection is not None:
            connection.close()
        database_module.db_connection = None
        for variable in ("DATABASE_PATH", "SECRET_KEY", "APP_ENV", "CORS_ORIGINS"):
            os.environ.pop(variable, None)
        self.temp_dir.cleanup()

    def assert_success(self, response, expected_status=200):
        self.assertEqual(expected_status, response.status_code, response.get_data(as_text=True))
        payload = response.get_json()
        self.assertIsInstance(payload, dict)
        self.assertTrue(payload.get("sucesso"), payload)
        return payload

    def get_product(self, product_id):
        response = self.client.get(f"/produtos/{product_id}")
        return self.assert_success(response)["dados"]

    def test_root_and_health_contracts(self):
        root = self.client.get("/")
        self.assertEqual(200, root.status_code)
        self.assertEqual("1.0.0", root.get_json()["versao"])
        self.assertEqual("/produtos", root.get_json()["endpoints"]["produtos"])

        health = self.client.get("/health")
        self.assertEqual(200, health.status_code)
        payload = health.get_json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("connected", payload["database"])
        self.assertEqual(10, payload["counts"]["produtos"])
        self.assertEqual(3, payload["counts"]["usuarios"])

    def test_catalog_crud_and_search_contract(self):
        listing = self.assert_success(self.client.get("/produtos"))["dados"]
        self.assertEqual(10, len(listing))

        created = self.assert_success(
            self.client.post(
                "/produtos",
                json={
                    "nome": "Produto E2E",
                    "descricao": "Contrato",
                    "preco": 25.5,
                    "estoque": 4,
                    "categoria": "livros",
                },
            ),
            201,
        )
        product_id = created["dados"]["id"]
        self.assertEqual("Produto E2E", self.get_product(product_id)["nome"])

        updated = self.client.put(
            f"/produtos/{product_id}",
            json={"nome": "Produto Atualizado", "preco": 30, "estoque": 3, "categoria": "livros"},
        )
        self.assert_success(updated)

        search = self.assert_success(self.client.get("/produtos/busca?q=Atualizado&categoria=livros"))
        self.assertEqual(1, search["total"])
        self.assertEqual(product_id, search["dados"][0]["id"])

        self.assert_success(self.client.delete(f"/produtos/{product_id}"))
        self.assertEqual(404, self.client.get(f"/produtos/{product_id}").status_code)

    def test_catalog_validation_and_missing_resources(self):
        invalid = self.client.post(
            "/produtos",
            json={"nome": "X", "preco": -1, "estoque": -1, "categoria": "invalida"},
        )
        self.assertEqual(400, invalid.status_code)
        self.assertEqual(404, self.client.get("/produtos/99999").status_code)
        self.assertEqual(404, self.client.get("/usuarios/99999").status_code)

    def test_user_creation_and_login_contract(self):
        created = self.assert_success(
            self.client.post(
                "/usuarios",
                json={"nome": "Pessoa E2E", "email": "pessoa.e2e@example.com", "senha": "senha-forte"},
            ),
            201,
        )
        self.assertIsInstance(created["dados"]["id"], int)

        login = self.assert_success(
            self.client.post(
                "/login",
                json={"email": "pessoa.e2e@example.com", "senha": "senha-forte"},
            )
        )
        self.assertEqual("pessoa.e2e@example.com", login["dados"]["email"])
        self.assertEqual(401, self.client.post("/login", json={"email": "pessoa.e2e@example.com", "senha": "errada"}).status_code)

    def test_order_listing_status_and_report_contract(self):
        created = self.assert_success(
            self.client.post(
                "/pedidos",
                json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 2}]},
            ),
            201,
        )
        order_id = created["dados"]["pedido_id"]
        self.assertAlmostEqual(11999.98, created["dados"]["total"], places=2)

        by_user = self.assert_success(self.client.get("/pedidos/usuario/1"))["dados"]
        self.assertEqual(order_id, by_user[0]["id"])
        self.assertEqual(2, by_user[0]["itens"][0]["quantidade"])

        all_orders = self.assert_success(self.client.get("/pedidos"))["dados"]
        self.assertEqual(1, len(all_orders))
        self.assert_success(self.client.put(f"/pedidos/{order_id}/status", json={"status": "aprovado"}))

        report = self.assert_success(self.client.get("/relatorios/vendas"))["dados"]
        self.assertEqual(1, report["total_pedidos"])
        self.assertEqual(1, report["pedidos_aprovados"])

    def test_admin_sql_console_is_not_public(self):
        response = self.client.post("/admin/query", json={"sql": "SELECT email, senha FROM usuarios"})
        self.assertIn(response.status_code, {401, 403, 404})

    def test_database_reset_is_not_public(self):
        self.client.get("/health")
        response = self.client.post("/admin/reset-db")
        self.assertIn(response.status_code, {401, 403, 404})
        self.assertEqual(10, len(self.assert_success(self.client.get("/produtos"))["dados"]))

    def test_login_resists_sql_injection(self):
        response = self.client.post("/login", json={"email": "' OR 1=1 --", "senha": "qualquer"})
        self.assertEqual(401, response.status_code)

    def test_product_text_with_apostrophe_is_persisted_literally(self):
        response = self.client.post(
            "/produtos",
            json={"nome": "Livro d'Água", "descricao": "Edição d'autor", "preco": 20, "estoque": 2, "categoria": "livros"},
        )
        payload = self.assert_success(response, 201)
        product = self.get_product(payload["dados"]["id"])
        self.assertEqual("Livro d'Água", product["nome"])
        self.assertEqual("Edição d'autor", product["descricao"])

    def test_password_is_hashed_and_never_serialized(self):
        raw_password = "senha-super-secreta"
        created = self.assert_success(
            self.client.post(
                "/usuarios",
                json={"nome": "Segurança", "email": "seguranca@example.com", "senha": raw_password},
            ),
            201,
        )
        user_id = created["dados"]["id"]

        users = self.assert_success(self.client.get("/usuarios"))["dados"]
        self.assertTrue(all("senha" not in user for user in users))
        user = self.assert_success(self.client.get(f"/usuarios/{user_id}"))["dados"]
        self.assertNotIn("senha", user)

        with sqlite3.connect(self.db_path) as connection:
            stored = connection.execute("SELECT senha FROM usuarios WHERE id = ?", (user_id,)).fetchone()[0]
        self.assertNotEqual(raw_password, stored)
        self.assertTrue(check_password_hash(stored, raw_password))

    def test_health_does_not_expose_secrets_or_internal_path(self):
        response = self.client.get("/health")
        self.assertEqual(200, response.status_code)
        payload = response.get_json()
        self.assertNotIn("secret_key", payload)
        self.assertNotIn("db_path", payload)
        self.assertNotEqual("minha-chave-super-secreta-123", self.application.config.get("SECRET_KEY"))

    def test_invalid_json_returns_client_error_without_internal_details(self):
        response = self.client.post("/login", data="null", content_type="application/json")
        self.assertEqual(400, response.status_code)
        payload = response.get_json()
        self.assertIn("erro", payload)
        self.assertNotIn("NoneType", payload["erro"])

    def test_non_positive_and_duplicate_quantities_do_not_change_stock(self):
        original_stock = self.get_product(1)["estoque"]

        negative = self.client.post(
            "/pedidos",
            json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": -2}]},
        )
        self.assertEqual(400, negative.status_code)
        self.assertEqual(original_stock, self.get_product(1)["estoque"])

        duplicate_overflow = self.client.post(
            "/pedidos",
            json={
                "usuario_id": 1,
                "itens": [
                    {"produto_id": 1, "quantidade": 6},
                    {"produto_id": 1, "quantidade": 6},
                ],
            },
        )
        self.assertEqual(400, duplicate_overflow.status_code)
        self.assertEqual(original_stock, self.get_product(1)["estoque"])

    def test_cancel_restores_stock_once_and_missing_order_is_404(self):
        original_stock = self.get_product(1)["estoque"]
        created = self.assert_success(
            self.client.post(
                "/pedidos",
                json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 2}]},
            ),
            201,
        )
        order_id = created["dados"]["pedido_id"]
        self.assertEqual(original_stock - 2, self.get_product(1)["estoque"])

        self.assert_success(self.client.put(f"/pedidos/{order_id}/status", json={"status": "cancelado"}))
        self.assertEqual(original_stock, self.get_product(1)["estoque"])
        self.assertEqual(400, self.client.put(f"/pedidos/{order_id}/status", json={"status": "cancelado"}).status_code)
        self.assertEqual(404, self.client.put("/pedidos/99999/status", json={"status": "aprovado"}).status_code)

    def test_referenced_product_cannot_be_deleted(self):
        self.assert_success(
            self.client.post(
                "/pedidos",
                json={"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": 1}]},
            ),
            201,
        )
        response = self.client.delete("/produtos/1")
        self.assertEqual(409, response.status_code)
        self.assertEqual("Notebook Gamer", self.get_product(1)["nome"])

    def test_debug_is_disabled_and_cors_is_restricted(self):
        self.assertFalse(self.application.debug)

        rejected = self.client.get("/", headers={"Origin": "https://maliciosa.exemplo"})
        self.assertNotEqual("https://maliciosa.exemplo", rejected.headers.get("Access-Control-Allow-Origin"))

        allowed = self.client.get("/", headers={"Origin": "https://cliente.exemplo"})
        allow_origin = allowed.headers.get("Access-Control-Allow-Origin")
        self.assertIn(allow_origin, {None, "https://cliente.exemplo"})


if __name__ == "__main__":
    unittest.main()
