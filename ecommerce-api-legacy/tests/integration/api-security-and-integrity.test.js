const assert = require('node:assert/strict');
const test = require('node:test');
const { createApp } = require('../../src/app');

async function fixture() {
  const app = await createApp({ port: 0, adminToken: 'integration-admin', database: { filename: ':memory:' } });
  const server = await new Promise((resolve) => {
    const listening = app.listen(0, '127.0.0.1', () => resolve(listening));
  });
  const baseUrl = `http://127.0.0.1:${server.address().port}`;
  return {
    app,
    baseUrl,
    close: async () => {
      await new Promise((resolve) => server.close(resolve));
      await app.locals.db.close();
    }
  };
}

test('operações administrativas exigem token válido', async () => {
  const context = await fixture();
  try {
    assert.equal((await fetch(`${context.baseUrl}/api/admin/financial-report`)).status, 401);
    assert.equal((await fetch(`${context.baseUrl}/api/users/1`, { method: 'DELETE' })).status, 401);
    const response = await fetch(`${context.baseUrl}/api/admin/financial-report`, { headers: { authorization: 'Bearer integration-admin' } });
    assert.equal(response.status, 200);
  } finally { await context.close(); }
});

test('exclusão autorizada não deixa matrículas ou pagamentos órfãos', async () => {
  const context = await fixture();
  try {
    const response = await fetch(`${context.baseUrl}/api/users/1`, { method: 'DELETE', headers: { authorization: 'Bearer integration-admin' } });
    assert.equal(response.status, 200);
    assert.equal((await context.app.locals.db.get('SELECT COUNT(*) AS count FROM enrollments WHERE user_id = 1')).count, 0);
    assert.equal((await context.app.locals.db.get('SELECT COUNT(*) AS count FROM payments')).count, 0);
  } finally { await context.close(); }
});

test('transação reverte todas as escritas quando uma etapa falha', async () => {
  const context = await fixture();
  try {
    await assert.rejects(context.app.locals.db.transaction(async (tx) => {
      await tx.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 2]);
      throw new Error('falha induzida');
    }), /falha induzida/);
    const row = await context.app.locals.db.get('SELECT COUNT(*) AS count FROM enrollments WHERE course_id = 2');
    assert.equal(row.count, 0);
  } finally { await context.close(); }
});
