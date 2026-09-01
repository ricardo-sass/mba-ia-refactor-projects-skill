class FinancialReportService {
  constructor(repository) { this.repository = repository; }
  buildReport() { return this.repository.buildReport(); }
}

module.exports = { FinancialReportService };
