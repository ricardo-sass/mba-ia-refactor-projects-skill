const assert = require('node:assert/strict');
const test = require('node:test');
const { hashPassword, verifyPassword } = require('../../src/models/users/passwordHash');
const { validateCheckoutPayload } = require('../../src/models/checkout/checkoutPayload');
const logger = require('../../src/shared/logger');

test('hash de senha usa salt e pode ser verificado', () => {
  const first = hashPassword('segredo');
  const second = hashPassword('segredo');
  assert.notEqual(first, second);
  assert.equal(verifyPassword('segredo', first), true);
  assert.equal(verifyPassword('errada', first), false);
});

test('payload inválido mantém Bad Request', () => {
  assert.deepEqual(validateCheckoutPayload({}), { error: 'Bad Request' });
  assert.deepEqual(validateCheckoutPayload({ usr: 'A', eml: 'a@b.c', c_id: '1', card: '4111' }), { error: 'Bad Request' });
});

test('logger remove dados sensíveis', () => {
  const original = console.log;
  let output = '';
  console.log = (line) => { output += line; };
  try { logger.info('teste', { card: '4111222233334444', password: 'segredo', paymentGatewayKey: 'chave', courseId: 1 }); }
  finally { console.log = original; }
  assert.equal(output.includes('4111222233334444'), false);
  assert.equal(output.includes('segredo'), false);
  assert.equal(output.includes('chave'), false);
  assert.equal(output.includes('courseId'), true);
});
