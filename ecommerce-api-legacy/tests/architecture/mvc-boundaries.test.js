const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

const rootDir = path.resolve(__dirname, '../..');
function files(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const target = path.join(dir, entry.name);
    return entry.isDirectory() ? files(target) : target.endsWith('.js') ? [target] : [];
  });
}
function assertAbsent(directory, pattern, message) {
  const offenders = files(path.join(rootDir, directory)).filter((file) => pattern.test(fs.readFileSync(file, 'utf8')));
  assert.deepEqual(offenders.map((file) => path.relative(rootDir, file)), [], message);
}

test('routes não acessam banco nem executam SQL', () => assertAbsent('src/routes', /sqlite3|SELECT |INSERT |UPDATE |DELETE |CREATE TABLE/i, 'SQL encontrado em route'));
test('repositories não conhecem Express ou HTTP', () => assertAbsent('src/repositories', /express|\breq\.|\bres\./, 'HTTP encontrado em repository'));
test('models não conhecem Express ou HTTP', () => assertAbsent('src/models', /express|\breq\.|\bres\./, 'HTTP encontrado em model'));
test('segredos legados não existem em src', () => assertAbsent('src', /pk_live_1234567890abcdef|senha_super_secreta_prod_123|admin_master/, 'segredo legado encontrado'));
test('não existe contêiner modules', () => assert.equal(fs.existsSync(path.join(rootDir, 'src/modules')), false));
