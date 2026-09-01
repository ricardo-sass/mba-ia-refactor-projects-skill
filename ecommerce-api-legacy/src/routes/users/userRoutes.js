const express = require('express');

function createUserRoutes(controller, authorizeAdmin) {
  const router = express.Router();
  router.delete('/users/:id', authorizeAdmin, async (req, res, next) => {
    try { res.send(await controller.deleteUser(req.params.id)); }
    catch (error) { next(error); }
  });
  return router;
}

module.exports = { createUserRoutes };
