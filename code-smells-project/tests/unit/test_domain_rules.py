import unittest
from unittest.mock import patch

from models.catalogo.validators import validate_product_payload
from models.pedidos.validators import validate_order_payload
from services.relatorios import SalesReportService
from shared.config import build_config
from shared.errors import ValidationError


class FakeReportRepository:
    def __init__(self, revenue, order_count=2):
        self.totals = {
            "faturamento": revenue,
            "total_pedidos": order_count,
            "pendentes": 1,
            "aprovados": 1,
            "cancelados": 0,
        }

    def sales_totals(self):
        return self.totals


class DomainRulesTest(unittest.TestCase):
    def test_duplicate_order_items_are_aggregated(self):
        user_id, items = validate_order_payload(
            {
                "usuario_id": 7,
                "itens": [
                    {"produto_id": 2, "quantidade": 3},
                    {"produto_id": 2, "quantidade": 4},
                ],
            }
        )
        self.assertEqual(7, user_id)
        self.assertEqual([{"produto_id": 2, "quantidade": 7}], items)

    def test_non_positive_order_quantity_is_rejected(self):
        for quantity in (0, -1):
            with self.subTest(quantity=quantity), self.assertRaises(ValidationError):
                validate_order_payload(
                    {"usuario_id": 1, "itens": [{"produto_id": 1, "quantidade": quantity}]}
                )

    def test_product_category_is_validated_for_create_and_update_payload(self):
        with self.assertRaises(ValidationError):
            validate_product_payload(
                {"nome": "Produto", "preco": 10, "estoque": 1, "categoria": "desconhecida"}
            )

    def test_sales_report_discount_thresholds_are_preserved(self):
        scenarios = [(500, 0), (2000, 40), (6000, 300), (12000, 1200)]
        for revenue, expected_discount in scenarios:
            with self.subTest(revenue=revenue):
                report = SalesReportService(FakeReportRepository(revenue)).build()
                self.assertEqual(expected_discount, report["desconto_aplicavel"])

    def test_production_requires_secret_and_boolean_config_is_normalized(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                build_config({"APP_ENV": "production"})
            config = build_config({"APP_ENV": "test", "DEBUG": "false", "TESTING": "true"})
        self.assertFalse(config["DEBUG"])
        self.assertTrue(config["TESTING"])


if __name__ == "__main__":
    unittest.main()
