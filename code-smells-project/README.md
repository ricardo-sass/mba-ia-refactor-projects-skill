# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro acesso, já com produtos e usuários de exemplo.

Em produção, defina obrigatoriamente `SECRET_KEY`. As configurações opcionais são:

- `APP_ENV`: ambiente da aplicação; o padrão é `development`;
- `DATABASE_PATH`: caminho do arquivo SQLite; o padrão é `loja.db`;
- `HOST`: interface do servidor de desenvolvimento; o padrão é `127.0.0.1`;
- `PORT`: porta do servidor de desenvolvimento; o padrão é `5000`;
- `DEBUG`: habilita debug apenas quando definido explicitamente;
- `CORS_ORIGINS`: lista de origens permitidas, separadas por vírgula.

O comando acima usa o servidor de desenvolvimento do Flask. Utilize um servidor WSGI adequado no ambiente de produção.

## Testes

Execute toda a suíte:

```bash
venv/bin/python -m unittest discover -v
```

Execute somente os contratos E2E usados na comparação antes/depois:

```bash
venv/bin/python -m unittest discover -v -s tests/e2e -p 'test_*.py'
```

Os testes usam arquivos SQLite temporários e não alteram `loja.db`.

## Arquitetura

As camadas principais são `models/`, `routes/` e `controllers/`, subdivididas pelos domínios `catalogo`, `usuarios`, `pedidos` e `relatorios`. `services/` concentra autenticação, transações e regras reutilizáveis; `repositories/` contém consultas e persistência complexas; `shared/` mantém apenas configuração, conexão e tratamento técnico de erros.
