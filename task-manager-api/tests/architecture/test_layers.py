import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


class ArchitectureTests(unittest.TestCase):
    def test_nao_existe_pasta_modules(self):
        self.assertFalse(any(path.is_dir() for path in ROOT.rglob("modules")))

    def test_camadas_possuem_subpastas_de_dominio_correspondentes(self):
        expected = {
            "models": {"tasks", "users", "categories"},
            "routes": {"tasks", "users", "categories", "reports"},
            "controllers": {"tasks", "users", "categories", "reports"},
            "services": {"tasks", "users", "reports"},
            "repositories": {"tasks", "users", "categories", "reports"},
        }
        for layer, domains in expected.items():
            actual = {
                path.name
                for path in (ROOT / layer).iterdir()
                if path.is_dir() and path.name != "__pycache__"
            }
            self.assertEqual(actual, domains, layer)

    def test_nao_ha_implementacoes_soltas_nas_camadas(self):
        for layer in ("models", "routes", "controllers", "services", "repositories"):
            loose_files = {
                path.name
                for path in (ROOT / layer).glob("*.py")
                if path.name != "__init__.py"
            }
            self.assertEqual(loose_files, set(), layer)

    def test_routes_nao_acessam_persistencia_ou_models(self):
        forbidden = ("models", "repositories", "shared.database", "sqlalchemy")
        for path in (ROOT / "routes").rglob("*.py"):
            modules = imported_modules(path)
            violations = {
                module for module in modules if module.startswith(forbidden)
            }
            self.assertEqual(violations, set(), str(path))
            self.assertNotIn("db.session", path.read_text(encoding="utf-8"))

    def test_models_e_repositories_nao_conhecem_http(self):
        for layer in ("models", "repositories"):
            for path in (ROOT / layer).rglob("*.py"):
                modules = imported_modules(path)
                self.assertFalse(any(module.startswith("flask") for module in modules), str(path))

    def test_controllers_nao_importam_flask_nem_outros_controllers(self):
        for path in (ROOT / "controllers").rglob("*.py"):
            modules = imported_modules(path)
            self.assertFalse(any(module.startswith("flask") for module in modules), str(path))
            if path.name != "__init__.py":
                self.assertFalse(
                    any(module.startswith("controllers.") for module in modules),
                    str(path),
                )

    def test_services_nao_dependem_do_protocolo_http(self):
        for path in (ROOT / "services").rglob("*.py"):
            modules = imported_modules(path)
            self.assertFalse(any(module.startswith("flask") for module in modules), str(path))

    def test_apis_obsoletas_nao_estao_na_aplicacao(self):
        application_roots = [
            ROOT / "app.py",
            ROOT / "seed.py",
            ROOT / "models",
            ROOT / "routes",
            ROOT / "controllers",
            ROOT / "services",
            ROOT / "repositories",
            ROOT / "shared",
        ]
        for root in application_roots:
            paths = [root] if root.is_file() else root.rglob("*.py")
            for path in paths:
                source = path.read_text(encoding="utf-8")
                self.assertNotIn("datetime.utcnow", source, str(path))
                self.assertNotIn(".query.get(", source, str(path))


if __name__ == "__main__":
    unittest.main()
