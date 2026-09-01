const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const rootDir = path.resolve(__dirname, '../..');
const mode = process.env.E2E_MODE || 'baseline';
const reportPath = process.env.E2E_REPORT || path.join(rootDir, 'reports', `e2e-${mode}-ecommerce-api-legacy.md`);
// O legado ignora PORT e escuta obrigatoriamente em 3000; a mesma porta é mantida
// nesta suíte antes/depois para que a linha de base seja executável sem alterar a aplicação.
const port = Number(process.env.PORT || 3000);
const baseUrl = `http://127.0.0.1:${port}`;
const results = [];
const logs = [];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function request(method, pathname, body) {
  const response = await fetch(`${baseUrl}${pathname}`, {
    method,
    headers: {
      authorization: 'Bearer e2e-admin-token',
      ...(body === undefined ? {} : { 'content-type': 'application/json' })
    },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const type = response.headers.get('content-type') || '';
  return {
    status: response.status,
    payload: type.includes('application/json') ? await response.json() : await response.text()
  };
}

async function scenario(name, test) {
  try {
    await test();
    results.push({ name, status: 'PASSOU', detail: 'Expectativas atendidas' });
  } catch (error) {
    results.push({ name, status: 'FALHOU', detail: error.message });
  }
}

async function waitUntilReady() {
  const deadline = Date.now() + 8000;
  while (Date.now() < deadline) {
    try {
      await request('GET', '/api/admin/financial-report');
      return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  throw new Error('Servidor não ficou pronto em 8 segundos');
}

async function run() {
  const server = spawn(process.execPath, ['src/app.js'], {
    cwd: rootDir,
    env: { ...process.env, PORT: String(port), PAYMENT_GATEWAY_KEY: 'e2e-fake-key', ADMIN_TOKEN: 'e2e-admin-token' },
    stdio: ['ignore', 'pipe', 'pipe']
  });
  server.stdout.on('data', (chunk) => logs.push(chunk.toString()));
  server.stderr.on('data', (chunk) => logs.push(chunk.toString()));

  try {
    await waitUntilReady();
    await scenario('Checkout aprovado preserva contrato', async () => {
      const response = await request('POST', '/api/checkout', { usr: 'Guilherme', eml: 'gui@fullcycle.com.br', pwd: 'senhaforte', c_id: 2, card: '4111222233334444' });
      assert(response.status === 200, `status ${response.status}`);
      assert(response.payload.msg === 'Sucesso', 'msg divergente');
      assert(typeof response.payload.enrollment_id === 'number', 'enrollment_id não numérico');
    });
    await scenario('Checkout recusado preserva contrato', async () => {
      const response = await request('POST', '/api/checkout', { usr: 'João', eml: 'joao@teste.com', pwd: '123', c_id: 1, card: '5111222233334444' });
      assert(response.status === 400, `status ${response.status}`);
      assert(response.payload === 'Pagamento recusado', 'mensagem divergente');
    });
    await scenario('Curso ausente preserva contrato', async () => {
      const response = await request('POST', '/api/checkout', { usr: 'Maria', eml: 'maria@teste.com', pwd: '123', c_id: 999, card: '4111222233334444' });
      assert(response.status === 404, `status ${response.status}`);
      assert(response.payload === 'Curso não encontrado', 'mensagem divergente');
    });
    await scenario('Payload inválido preserva contrato', async () => {
      const response = await request('POST', '/api/checkout', {});
      assert(response.status === 400, `status ${response.status}`);
      assert(response.payload === 'Bad Request', 'mensagem divergente');
    });
    await scenario('Relatório financeiro preserva schema', async () => {
      const response = await request('GET', '/api/admin/financial-report');
      assert(response.status === 200, `status ${response.status}`);
      assert(Array.isArray(response.payload), 'resposta não é array');
      const course = response.payload.find((item) => item.course === 'Clean Architecture');
      assert(course && Array.isArray(course.students), 'curso seed ou students ausente');
    });
    await scenario('Exclusão preserva resposta textual', async () => {
      const response = await request('DELETE', '/api/users/1');
      assert(response.status === 200, `status ${response.status}`);
      assert(response.payload === 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.', 'mensagem divergente');
    });
    await scenario('Logs não expõem cartão nem chave', async () => {
      await new Promise((resolve) => setTimeout(resolve, 100));
      const output = logs.join('');
      assert(!output.includes('4111222233334444'), 'cartão completo exposto');
      assert(!output.includes('e2e-fake-key') && !output.includes('pk_live_'), 'chave exposta');
    });
  } finally {
    server.kill('SIGTERM');
    await new Promise((resolve) => server.once('exit', resolve));
  }
}

function writeReport() {
  const counts = results.reduce((total, item) => ({ ...total, [item.status]: (total[item.status] || 0) + 1 }), {});
  const safeLogs = logs.join('').replace(/\b\d{13,19}\b/g, '[CARTÃO_MASCARADO]').replace(/pk_live_[\w-]+/g, '[SEGREDO_MASCARADO]');
  const lines = [
    `# E2E ${mode === 'baseline' ? 'Baseline' : 'Após Refatoração'} - ecommerce-api-legacy`, '',
    `- **Modo:** ${mode}`, `- **Executor:** Node.js ${process.version} com fetch nativo`,
    `- **Comando:** E2E_MODE=${mode} E2E_REPORT=${path.relative(rootDir, reportPath)} node tests/e2e/run-e2e.js`,
    `- **Ambiente:** execução nativa isolada em ${baseUrl} com SQLite em memória`,
    `- **Resumo:** PASSOU=${counts.PASSOU || 0}; FALHOU=${counts.FALHOU || 0}; NÃO EXECUTADO=0`, '',
    '| Cenário | Resultado | Evidência |', '|---|---|---|',
    ...results.map((item) => `| ${item.name} | ${item.status} | ${item.detail.replace(/\|/g, '\\|')} |`), '',
    '## Logs capturados (dados sensíveis mascarados)', '', '```text', safeLogs.trim(), '```', ''
  ];
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, lines.join('\n'));
}

run().catch((error) => results.push({ name: 'Preparação da suíte', status: 'FALHOU', detail: error.message })).finally(() => {
  writeReport();
  process.exitCode = results.some((item) => item.status === 'FALHOU') ? 1 : 0;
});
