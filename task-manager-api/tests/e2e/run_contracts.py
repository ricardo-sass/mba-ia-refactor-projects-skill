"""Suíte de contrato E2E reutilizada antes e depois da refatoração."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT / "venv" / "bin" / "python"


@dataclass
class HttpResponse:
    status: int
    body: Any
    content_type: str


@dataclass
class ScenarioResult:
    name: str
    kind: str
    status: str
    detail: str


class WsgiTransport:
    """Transporta requisições pelo limite WSGI sem abrir sockets no host."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def request(
        self,
        method: str,
        path: str,
        data: Any,
        headers: dict[str, str],
    ) -> HttpResponse:
        response = self.client.open(path, method=method, json=data, headers=headers)
        body = response.get_json(silent=True)
        if body is None:
            body = response.get_data(as_text=True)
        return HttpResponse(response.status_code, body, response.mimetype)


class ContractSuite:
    def __init__(self, transport: WsgiTransport) -> None:
        self.transport = transport
        self.results: list[ScenarioResult] = []
        self.token: str | None = None
        self.created_category_id: int | None = None
        self.created_user_id: int | None = None
        self.created_task_id: int | None = None

    def request(
        self,
        method: str,
        path: str,
        data: Any = None,
        *,
        authenticated: bool = True,
        token: str | None = None,
    ) -> HttpResponse:
        headers = {"Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        selected_token = token if token is not None else self.token
        if authenticated and selected_token:
            headers["Authorization"] = f"Bearer {selected_token}"

        return self.transport.request(method, path, data, headers)

    def scenario(self, name: str, kind: str, check: Callable[[], None]) -> None:
        try:
            check()
        except Exception as error:
            self.results.append(ScenarioResult(name, kind, "FALHOU", str(error)))
        else:
            self.results.append(ScenarioResult(name, kind, "PASSOU", "expectativa atendida"))

    @staticmethod
    def assert_status(response: HttpResponse, *expected: int) -> None:
        if response.status not in expected:
            raise AssertionError(
                f"status {response.status}, esperado {expected}; resposta={response.body!r}"
            )

    @staticmethod
    def assert_object(response: HttpResponse) -> dict[str, Any]:
        if not isinstance(response.body, dict):
            raise AssertionError(f"objeto JSON esperado; resposta={response.body!r}")
        return response.body

    def run(self) -> list[ScenarioResult]:
        self.scenario("raiz", "invariante", self._root)
        self.scenario("health", "invariante", self._health)
        self.scenario("login válido", "invariante", self._login)
        self.scenario("login inválido", "invariante", self._invalid_login)
        self.scenario("login não expõe senha", "defeito", self._login_hides_password)
        self.scenario("listagem de tasks", "invariante", self._list_tasks)
        self.scenario("detalhe de task", "invariante", self._task_detail)
        self.scenario("task ausente", "invariante", self._missing_task)
        self.scenario("busca de tasks", "invariante", self._search_tasks)
        self.scenario("filtro numérico inválido", "defeito", self._invalid_numeric_filter)
        self.scenario("estatísticas de tasks", "invariante", self._task_stats)
        self.scenario("listagem de usuários", "invariante", self._list_users)
        self.scenario("detalhe de usuário", "invariante", self._user_detail)
        self.scenario("detalhe não expõe senha", "defeito", self._user_hides_password)
        self.scenario("tasks do usuário", "invariante", self._user_tasks)
        self.scenario("resumo de relatórios", "invariante", self._summary_report)
        self.scenario("relatório por usuário", "invariante", self._user_report)
        self.scenario("listagem de categorias", "invariante", self._list_categories)
        self.scenario("mutação anônima bloqueada", "defeito", self._anonymous_mutation)
        self.scenario("token forjado bloqueado", "defeito", self._forged_token)
        self.scenario("criação de categoria", "invariante", self._create_category)
        self.scenario("atualização de categoria", "invariante", self._update_category)
        self.scenario("criação de usuário", "invariante", self._create_user)
        self.scenario("criação não expõe senha", "defeito", self._created_user_hides_password)
        self.scenario("criação de task associada", "invariante", self._create_task)
        self.scenario("atualização de task", "invariante", self._update_task)
        self.scenario("body inválido retorna JSON 400", "defeito", self._invalid_body)
        self.scenario("exclusão de task", "invariante", self._delete_task)
        self.scenario("exclusão de usuário", "invariante", self._delete_user)
        self.scenario("exclusão de categoria", "invariante", self._delete_category)
        return self.results

    def _root(self) -> None:
        response = self.request("GET", "/", authenticated=False)
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert body["message"] == "Task Manager API" and body["version"] == "1.0"

    def _health(self) -> None:
        response = self.request("GET", "/health", authenticated=False)
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert body["status"] == "ok" and isinstance(body["timestamp"], str)

    def _login(self) -> None:
        response = self.request(
            "POST",
            "/login",
            {"email": "joao@email.com", "password": "1234"},
            authenticated=False,
        )
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert isinstance(body.get("token"), str) and body["token"]
        self.token = body["token"]

    def _invalid_login(self) -> None:
        response = self.request(
            "POST",
            "/login",
            {"email": "joao@email.com", "password": "incorreta"},
            authenticated=False,
        )
        self.assert_status(response, 401)
        assert self.assert_object(response)["error"] == "Credenciais inválidas"

    def _login_hides_password(self) -> None:
        response = self.request(
            "POST",
            "/login",
            {"email": "joao@email.com", "password": "1234"},
            authenticated=False,
        )
        self.assert_status(response, 200)
        assert "password" not in self.assert_object(response)["user"]

    def _list_tasks(self) -> None:
        response = self.request("GET", "/tasks")
        self.assert_status(response, 200)
        assert isinstance(response.body, list) and len(response.body) >= 10
        expected = {"id", "title", "status", "priority", "overdue", "tags"}
        assert expected.issubset(response.body[0])

    def _task_detail(self) -> None:
        response = self.request("GET", "/tasks/1")
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert body["id"] == 1 and "overdue" in body

    def _missing_task(self) -> None:
        response = self.request("GET", "/tasks/999999")
        self.assert_status(response, 404)
        assert self.assert_object(response)["error"] == "Task não encontrada"

    def _search_tasks(self) -> None:
        response = self.request("GET", "/tasks/search?status=pending&priority=1")
        self.assert_status(response, 200)
        assert isinstance(response.body, list) and response.body
        assert all(item["status"] == "pending" and item["priority"] == 1 for item in response.body)

    def _invalid_numeric_filter(self) -> None:
        response = self.request("GET", "/tasks/search?priority=abc")
        self.assert_status(response, 400)
        assert response.content_type == "application/json"

    def _task_stats(self) -> None:
        response = self.request("GET", "/tasks/stats")
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert {"total", "pending", "done", "overdue", "completion_rate"}.issubset(body)

    def _list_users(self) -> None:
        response = self.request("GET", "/users")
        self.assert_status(response, 200)
        assert isinstance(response.body, list) and len(response.body) >= 3
        assert all("password" not in user for user in response.body)

    def _user_detail(self) -> None:
        response = self.request("GET", "/users/1")
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert body["id"] == 1 and isinstance(body["tasks"], list)

    def _user_hides_password(self) -> None:
        response = self.request("GET", "/users/1")
        self.assert_status(response, 200)
        assert "password" not in self.assert_object(response)

    def _user_tasks(self) -> None:
        response = self.request("GET", "/users/1/tasks")
        self.assert_status(response, 200)
        assert isinstance(response.body, list) and response.body
        assert {"id", "title", "overdue"}.issubset(response.body[0])

    def _summary_report(self) -> None:
        response = self.request("GET", "/reports/summary")
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert {"overview", "tasks_by_status", "overdue", "user_productivity"}.issubset(body)

    def _user_report(self) -> None:
        response = self.request("GET", "/reports/user/1")
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert body["user"]["id"] == 1 and "completion_rate" in body["statistics"]

    def _list_categories(self) -> None:
        response = self.request("GET", "/categories")
        self.assert_status(response, 200)
        assert isinstance(response.body, list) and len(response.body) >= 4
        assert "task_count" in response.body[0]

    def _anonymous_mutation(self) -> None:
        response = self.request(
            "POST",
            "/tasks",
            {"title": "Tentativa anônima"},
            authenticated=False,
        )
        self.assert_status(response, 401, 403)

    def _forged_token(self) -> None:
        response = self.request(
            "POST",
            "/tasks",
            {"title": "Tentativa com token forjado"},
            token="fake-jwt-token-999999",
        )
        self.assert_status(response, 401, 403)

    def _create_category(self) -> None:
        response = self.request(
            "POST",
            "/categories",
            {"name": "E2E", "description": "Categoria temporária", "color": "#123456"},
        )
        self.assert_status(response, 201)
        body = self.assert_object(response)
        assert body["name"] == "E2E"
        self.created_category_id = body["id"]

    def _update_category(self) -> None:
        assert self.created_category_id is not None
        response = self.request(
            "PUT",
            f"/categories/{self.created_category_id}",
            {"description": "Categoria atualizada"},
        )
        self.assert_status(response, 200)
        assert self.assert_object(response)["description"] == "Categoria atualizada"

    def _create_user(self) -> None:
        response = self.request(
            "POST",
            "/users",
            {
                "name": "Usuário E2E",
                "email": "e2e@example.com",
                "password": "senha-e2e",
                "role": "user",
            },
        )
        self.assert_status(response, 201)
        body = self.assert_object(response)
        assert body["email"] == "e2e@example.com"
        self.created_user_id = body["id"]

    def _created_user_hides_password(self) -> None:
        response = self.request("GET", f"/users/{self.created_user_id}")
        self.assert_status(response, 200)
        assert "password" not in self.assert_object(response)

    def _create_task(self) -> None:
        assert self.created_category_id is not None and self.created_user_id is not None
        response = self.request(
            "POST",
            "/tasks",
            {
                "title": "Task do E2E",
                "description": "Criada pelo contrato",
                "status": "pending",
                "priority": 2,
                "user_id": self.created_user_id,
                "category_id": self.created_category_id,
                "due_date": "2030-01-02",
                "tags": ["e2e", "contrato"],
            },
        )
        self.assert_status(response, 201)
        body = self.assert_object(response)
        assert body["title"] == "Task do E2E" and body["tags"] == ["e2e", "contrato"]
        self.created_task_id = body["id"]

    def _update_task(self) -> None:
        assert self.created_task_id is not None
        response = self.request(
            "PUT",
            f"/tasks/{self.created_task_id}",
            {"status": "in_progress", "priority": 1},
        )
        self.assert_status(response, 200)
        body = self.assert_object(response)
        assert body["status"] == "in_progress" and body["priority"] == 1

    def _invalid_body(self) -> None:
        response = self.request("POST", "/tasks", ["não", "é", "objeto"])
        self.assert_status(response, 400)
        assert response.content_type == "application/json"

    def _delete_task(self) -> None:
        assert self.created_task_id is not None
        response = self.request("DELETE", f"/tasks/{self.created_task_id}")
        self.assert_status(response, 200)
        self.assert_status(self.request("GET", f"/tasks/{self.created_task_id}"), 404)

    def _delete_user(self) -> None:
        assert self.created_user_id is not None
        response = self.request("DELETE", f"/users/{self.created_user_id}")
        self.assert_status(response, 200)
        self.assert_status(self.request("GET", f"/users/{self.created_user_id}"), 404)

    def _delete_category(self) -> None:
        assert self.created_category_id is not None
        response = self.request("DELETE", f"/categories/{self.created_category_id}")
        self.assert_status(response, 200)


def copy_application(destination: Path) -> None:
    root = ROOT.resolve()

    def ignored(directory: str, names: list[str]) -> set[str]:
        ignored_names = {
            name
            for name in names
            if name == "__pycache__" or name.endswith((".db", ".pyc"))
        }
        if Path(directory).resolve() == root:
            ignored_names.update(
                name
                for name in names
                if name in {".git", ".agents", ".codex", "venv", "reports", "tests", "instance"}
            )
        return ignored_names

    shutil.copytree(ROOT, destination, dirs_exist_ok=True, ignore=ignored)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("baseline", "after"), required=True)
    parser.add_argument("--json-output")
    args = parser.parse_args()

    if not PYTHON.exists():
        raise SystemExit(f"runtime não encontrado: {PYTHON}")

    with tempfile.TemporaryDirectory(prefix="task-manager-e2e-") as temp_dir:
        temp = Path(temp_dir)
        source = temp / "app-source"
        copy_application(source)

        seed = subprocess.run(
            [str(PYTHON), str(source / "seed.py")],
            cwd=source,
            capture_output=True,
            check=False,
            timeout=30,
        )
        if seed.returncode != 0:
            sys.stderr.write(seed.stderr.decode("utf-8", errors="replace"))
            return 2

        sys.path.insert(0, str(source))
        from app import app

        app.config.update(TESTING=False)
        client = app.test_client()
        readiness = client.get("/health")
        if readiness.status_code != 200:
            raise RuntimeError(f"health falhou com status {readiness.status_code}")
        results = ContractSuite(WsgiTransport(client)).run()

        payload = {
            "stage": args.stage,
            "results": [asdict(result) for result in results],
            "summary": {
                "passed": sum(result.status == "PASSOU" for result in results),
                "failed": sum(result.status == "FALHOU" for result in results),
                "invariant_failed": sum(
                    result.status == "FALHOU" and result.kind == "invariante"
                    for result in results
                ),
                "defect_failed": sum(
                    result.status == "FALHOU" and result.kind == "defeito"
                    for result in results
                ),
            },
        }
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        print(serialized)
        if args.json_output:
            Path(args.json_output).write_text(serialized + "\n", encoding="utf-8")

        if payload["summary"]["invariant_failed"]:
            return 1
        if args.stage == "after" and payload["summary"]["failed"]:
            return 1
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
