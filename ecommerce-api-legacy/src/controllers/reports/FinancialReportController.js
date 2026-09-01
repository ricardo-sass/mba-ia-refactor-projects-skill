class FinancialReportController {
  constructor(service) { this.service = service; }
  getFinancialReport() { return this.service.buildReport(); }
}

module.exports = { FinancialReportController };
