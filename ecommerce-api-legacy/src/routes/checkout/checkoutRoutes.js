const express = require('express');

function createCheckoutRoutes(controller) {
  const router = express.Router();
  router.post('/checkout', async (req, res, next) => {
    try { res.status(200).json(await controller.checkout(req.body)); }
    catch (error) { next(error); }
  });
  return router;
}

module.exports = { createCheckoutRoutes };
