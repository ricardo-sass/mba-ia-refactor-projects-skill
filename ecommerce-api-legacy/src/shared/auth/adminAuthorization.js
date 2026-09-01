const crypto = require('node:crypto');
const { AppError } = require('../errors/AppError');

function createAdminAuthorization(expectedToken) {
  return function authorizeAdmin(req, res, next) {
    const suppliedToken = req.get('authorization')?.replace(/^Bearer\s+/i, '');
    const valid = expectedToken && suppliedToken && expectedToken.length === suppliedToken.length
      && crypto.timingSafeEqual(Buffer.from(expectedToken), Buffer.from(suppliedToken));
    if (!valid) return next(new AppError(401, 'Unauthorized'));
    return next();
  };
}

module.exports = { createAdminAuthorization };
