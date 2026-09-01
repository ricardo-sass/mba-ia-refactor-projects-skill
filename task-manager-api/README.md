# task-manager-api

API de Task Manager em Python/Flask organizada em MVC por domínios. As camadas principais `models/`, `routes/` e `controllers/` possuem áreas correspondentes para tarefas, usuários, categorias e relatórios. Services e Repositories são usados apenas nas regras, integrações e consultas que precisam deles.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

Configure `SECRET_KEY` no ambiente para manter tokens válidos entre reinicializações. `DATABASE_URL`, `TOKEN_MAX_AGE`, `APP_HOST`, `APP_PORT` e `FLASK_DEBUG` também podem ser definidos por ambiente; debug fica desabilitado por padrão.

## Autenticação

`GET /`, `GET /health` e `POST /login` são públicos. Os demais endpoints exigem o header `Authorization: Bearer <token>` obtido no login. Operações de categorias e relatórios exigem papel `admin` ou `manager`; criação e exclusão de usuários exigem `admin`.

Senhas legadas em MD5 são aceitas apenas para uma migração transparente no primeiro login válido e imediatamente substituídas por password hashing adaptativo. Novas senhas precisam ter ao menos oito caracteres.

## Testes

```bash
python -m unittest discover -s tests -p 'test*.py' -v
python tests/e2e/run_contracts.py --stage after
```

A suíte E2E cria uma cópia temporária da aplicação e um SQLite exclusivo; ela não altera o banco local.
