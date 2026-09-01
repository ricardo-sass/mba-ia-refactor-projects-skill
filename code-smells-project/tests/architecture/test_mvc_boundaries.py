import ast
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def python_files(directory):
    return [path for path in (PROJECT_ROOT / directory).rglob("*.py") if path.name != "__init__.py"]


def imported_modules(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


class MvcBoundariesTest(unittest.TestCase):
    def test_required_layers_and_domains_exist(self):
        domains = {"catalogo", "usuarios", "pedidos", "relatorios"}
        for layer in ("models", "routes", "controllers"):
            self.assertTrue((PROJECT_ROOT / layer).is_dir())
            self.assertTrue(domains.issubset({path.name for path in (PROJECT_ROOT / layer).iterdir()}))
        self.assertFalse((PROJECT_ROOT / "modules").exists())
        self.assertFalse((PROJECT_ROOT / "models.py").exists())
        self.assertFalse((PROJECT_ROOT / "controllers.py").exists())

    def test_routes_depend_only_on_http_and_controllers(self):
        forbidden_prefixes = ("sqlite3", "shared.database", "models", "repositories", "services")
        for path in python_files("routes"):
            with self.subTest(path=path):
                imports = imported_modules(path)
                self.assertFalse(
                    any(module.startswith(forbidden_prefixes) for module in imports),
                    imports,
                )

    def test_controllers_do_not_depend_on_http_or_database_driver(self):
        forbidden_prefixes = ("flask", "sqlite3", "shared.database", "repositories")
        for path in python_files("controllers"):
            with self.subTest(path=path):
                imports = imported_modules(path)
                self.assertFalse(
                    any(module.startswith(forbidden_prefixes) for module in imports),
                    imports,
                )

    def test_models_and_repositories_do_not_depend_on_http(self):
        for layer in ("models", "repositories"):
            for path in python_files(layer):
                with self.subTest(path=path):
                    self.assertFalse(any(module.startswith("flask") for module in imported_modules(path)))

    def test_sql_is_confined_to_models_repositories_and_shared_database(self):
        sql_tokens = ("SELECT ", "INSERT ", "UPDATE ", "DELETE ", "CREATE TABLE")
        for layer in ("routes", "controllers", "services"):
            for path in python_files(layer):
                with self.subTest(path=path):
                    source = path.read_text(encoding="utf-8").upper()
                    self.assertFalse(any(token in source for token in sql_tokens))


if __name__ == "__main__":
    unittest.main()
