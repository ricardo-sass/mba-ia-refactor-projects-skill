# Playbook De Refatoração

Aplicar somente transformações ligadas a achados aprovados. Os exemplos ilustram o padrão; adaptar a sintaxe e as bibliotecas à stack detectada.

## Sumário

1. Parametrizar SQL
2. Extrair configuração e segredos
3. Tornar senhas resistentes
4. Afinar rotas e extrair Controller
5. Delimitar transação
6. Eliminar N+1
7. Centralizar validação
8. Centralizar erros
9. Substituir estado global
10. Modernizar API obsoleta
11. Preservar integridade em delete
12. Criar fábrica de aplicação
13. Extrair Service
14. Extrair Repository
15. Adicionar teste de responsabilidades MVC
16. Organizar domínios nas camadas MVC

## 1. Parametrizar SQL

Antes:

```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

Depois:

```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

Usar placeholders do driver. Parâmetros não substituem allowlist para nomes de coluna ou comandos.

## 2. Extrair Configuração E Segredos

Antes:

```javascript
const paymentKey = "pk_live_value";
```

Depois:

```javascript
const paymentKey = process.env.PAYMENT_GATEWAY_KEY;
if (!paymentKey) throw new Error('PAYMENT_GATEWAY_KEY is required');
```

Fornecer `.env.example` apenas com nomes e valores fictícios quando o projeto usa esse padrão. Não mover o segredo real para outro arquivo versionado.

## 3. Tornar Senhas Resistentes

Antes:

```python
self.password = hashlib.md5(raw.encode()).hexdigest()
```

Depois:

```python
from werkzeug.security import generate_password_hash
self.password = generate_password_hash(raw)
```

Usar o verificador correspondente e planejar compatibilidade/migração para hashes existentes.

## 4. Afinar Rotas E Extrair Controller

Antes:

```javascript
app.post('/orders', async (req, res) => {
  const total = calculate(req.body.items);
  await db.save({ total });
  res.status(201).json({ total });
});
```

Depois:

```javascript
router.post('/orders', async (req, res, next) => {
  try { res.status(201).json(await orderController.create(req.body)); }
  catch (error) { next(error); }
});
```

Manter cálculo e persistência no controller/service, não no router.

## 5. Delimitar Transação

Antes:

```python
order_id = insert_order(data)
insert_items(order_id, items)
db.commit()
```

Depois:

```python
try:
    order_id = insert_order(data)
    insert_items(order_id, items)
    db.commit()
except Exception:
    db.rollback()
    raise
```

Em APIs assíncronas, promisificar ou usar driver com suporte transacional e garantir rollback em cada rejeição.

## 6. Eliminar N+1

Antes:

```python
for user in users:
    user.tasks = Task.query.filter_by(user_id=user.id).all()
```

Depois:

```python
users = db.session.execute(
    select(User).options(selectinload(User.tasks))
).scalars().all()
```

Para relatórios, preferir `JOIN`, `GROUP BY` e agregações em uma consulta.

## 7. Centralizar Validação

Antes:

```python
if status not in ['pending', 'done']:
    return {'error': 'invalid'}, 400
```

Depois:

```python
payload, error = validate_task_payload(request.get_json(silent=True))
if error:
    raise ValidationError(error)
```

Reutilizar constantes e schema entre criação/atualização; preservar mensagens externas quando fizerem parte do contrato.

## 8. Centralizar Erros

Antes:

```javascript
if (err) return res.status(500).send(err.message);
```

Depois:

```javascript
app.use((error, req, res, next) => {
  logger.error({ error, path: req.path }, 'request failed');
  res.status(error.status || 500).json({ error: error.publicMessage || 'Internal error' });
});
```

Não retornar stack, SQL, caminhos ou segredos.

## 9. Substituir Estado Global

Antes:

```javascript
const cache = {};
module.exports = { cache };
```

Depois:

```javascript
function createApp({ cache, repository }) {
  const controller = new Controller({ cache, repository });
  return buildRoutes(controller);
}
```

Injetar dependência com ciclo de vida explícito. Para cache compartilhado real, usar implementação adequada e limites.

## 10. Modernizar API Obsoleta

Antes:

```python
user = User.query.get(user_id)
```

Depois:

```python
user = db.session.get(User, user_id)
```

Confirmar suporte na versão declarada e executar testes para detectar diferenças de retorno, exceção e lazy loading.

## 11. Preservar Integridade Em Delete

Antes:

```javascript
db.run('DELETE FROM users WHERE id = ?', [id]);
```

Depois:

```javascript
await transaction(async (tx) => {
  await tx.run('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [id]);
  await tx.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
  await tx.run('DELETE FROM users WHERE id = ?', [id]);
});
```

Preferir foreign keys e cascade quando a regra de domínio permitir.

## 12. Criar Fábrica De Aplicação

Antes:

```python
app = Flask(__name__)
db.init_app(app)
db.create_all()
```

Depois:

```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(config or {})
    db.init_app(app)
    register_routes(app)
    return app
```

Executar criação/migração de schema por comando explícito quando possível. A factory facilita teste isolado e injeção de configuração.

## 13. Extrair Service

Antes:

```python
def create_route():
    data = validate(request.get_json())
    record = repository.save(data)
    notifier.send(record)
    return jsonify(record)
```

Depois:

```python
def create_route():
    result = controller.create(request.get_json())
    return jsonify(result)

class CreationService:
    def create(self, data):
        validated = validate(data)
        record = self.repository.save(validated)
        self.notifier.send(record)
        return record
```

Mover regra reutilizável, integração e limite transacional para o Service. Manter parsing e resposta HTTP na Route/Controller. Não extrair Service que apenas repasse uma chamada.

## 14. Extrair Repository

Antes:

```python
def find_controller(record_id):
    row = db.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
    return jsonify(dict(row))
```

Depois:

```python
class RecordRepository:
    def find_by_id(self, record_id):
        return self.db.execute(
            "SELECT * FROM records WHERE id = ?", (record_id,)
        ).fetchone()
```

Mover SQL, queries ORM complexas e detalhes transacionais para o Repository do domínio. Permitir persistência simples no Model quando essa for a convenção do framework; não exigir Repository vazio.

## 15. Adicionar Teste De Responsabilidades MVC

Antes:

```python
from flask import request
from sqlalchemy import text
```

Depois:

```python
def test_routes_do_not_import_database():
    assert_no_imports("src/routes", {"sqlalchemy", "sqlite3"})

def test_models_do_not_import_http():
    assert_no_imports("src/models", {"flask", "express"})
```

Configurar ferramenta estática ou teste simples para impedir SQL em Routes, HTTP em Models/Repositories e imports indevidos entre domínios. Adaptar os caminhos à estrutura real e evitar regras baseadas apenas no nome do arquivo.

## 16. Organizar Domínios Nas Camadas MVC

Antes:

```text
src/
  controllers/{domain_a_controller,domain_b_controller}
  services/{domain_a_service,domain_b_service}
  models/{domain_a_model,domain_b_model}
  repositories/{domain_a_repository,domain_b_repository}
```

Depois:

```text
src/
  models/{domain_a,domain_b}
  views/ ou routes/{domain_a,domain_b}
  controllers/{domain_a,domain_b}
  services/{domain_a,domain_b}
  repositories/{domain_a,domain_b}
  shared/{config,database,errors}
```

Identificar primeiro os limites por regras, fluxos e dados alterados em conjunto. Manter as camadas MVC como pastas principais e mover cada arquivo para a subpasta de seu domínio na camada correspondente. Preservar contratos e histórico de testes. Omitir `services`, `repositories` ou subpastas vazias quando não houver responsabilidade concreta.

Não criar `modules/`. Expor Services ou funções claramente definidas para colaboração entre domínios. Não importar Controller de outra área. Compartilhar conexão, logging e configuração quando forem recursos técnicos; manter regras e Repositories nas subpastas de seu domínio.

## Ordem Recomendada

1. Fixar contratos com testes.
2. Criar e executar a linha de base E2E contra o código original.
3. Extrair configuração e inicialização da aplicação.
4. Delimitar domínios e distribuí-los em subpastas correspondentes de Models, Views/Routes e Controllers.
5. Corrigir vulnerabilidades sem alterar a forma da API.
6. Extrair Models/Repositories e transações na subpasta do domínio proprietário.
7. Extrair Controllers/Services e afinar Routes na subpasta correspondente de cada camada.
8. Centralizar validação e erros realmente transversais.
9. Otimizar queries e modernizar APIs.
10. Adicionar testes de responsabilidades MVC e separação entre domínios.
11. Reconstruir o ambiente e reexecutar auditoria e a mesma suíte E2E.
