const logger = require('../logger');

function errorMiddleware(err, req, res, next) {
  if (res.headersSent) return next(err);
  if (err.statusCode && err.publicMessage) return res.status(err.statusCode).send(err.publicMessage);
  logger.error('Falha inesperada na requisição', { path: req.path, error: err });
  return res.status(500).send('Erro DB');
}

module.exports = { errorMiddleware };
