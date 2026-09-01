const crypto = require('node:crypto');

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password || '123456', salt, 64).toString('hex');
  return `scrypt:${salt}:${hash}`;
}

function verifyPassword(password, encoded) {
  const [algorithm, salt, stored] = String(encoded).split(':');
  if (algorithm !== 'scrypt' || !salt || !stored) return false;
  const candidate = crypto.scryptSync(password, salt, 64);
  const expected = Buffer.from(stored, 'hex');
  return candidate.length === expected.length && crypto.timingSafeEqual(candidate, expected);
}

module.exports = { hashPassword, verifyPassword };
