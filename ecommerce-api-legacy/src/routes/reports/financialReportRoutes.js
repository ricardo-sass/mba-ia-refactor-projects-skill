const express = require('express');

function createFinancialReportRoutes(controller, authorizeAdmin) {
  const router = express.Router();
  router.get('/admin/financial-report', authorizeAdmin, async (req, res, next) => {
    try { res.json(await controller.getFinancialReport()); }
    catch (error) { next(error); }
  });
  return router;
}

module.exports = { createFinancialReportRoutes };
