const express = require('express');
const { config } = require('./shared/config');
const logger = require('./shared/logger');
const { createSqliteDatabase } = require('./shared/database/sqliteDatabase');
const { initializeDatabase } = require('./shared/database/schema');
const { errorMiddleware } = require('./shared/errors/errorMiddleware');
const { createAdminAuthorization } = require('./shared/auth/adminAuthorization');
const { CourseRepository } = require('./repositories/checkout/CourseRepository');
const { UserRepository } = require('./repositories/checkout/UserRepository');
const { CheckoutRepository } = require('./repositories/checkout/CheckoutRepository');
const { FinancialReportRepository } = require('./repositories/reports/FinancialReportRepository');
const { UserDeletionRepository } = require('./repositories/users/UserDeletionRepository');
const { CheckoutService } = require('./services/checkout/CheckoutService');
const { FinancialReportService } = require('./services/reports/FinancialReportService');
const { UserDeletionService } = require('./services/users/UserDeletionService');
const { CheckoutController } = require('./controllers/checkout/CheckoutController');
const { FinancialReportController } = require('./controllers/reports/FinancialReportController');
const { UserController } = require('./controllers/users/UserController');
const { createCheckoutRoutes } = require('./routes/checkout/checkoutRoutes');
const { createFinancialReportRoutes } = require('./routes/reports/financialReportRoutes');
const { createUserRoutes } = require('./routes/users/userRoutes');

async function createApp(appConfig = config) {
  const app = express();
  const db = createSqliteDatabase(appConfig.database.filename);
  await initializeDatabase(db);

  const checkoutService = new CheckoutService({
    courseRepository: new CourseRepository(db),
    userRepository: new UserRepository(db),
    checkoutRepository: new CheckoutRepository(db),
    logger
  });
  const reportService = new FinancialReportService(new FinancialReportRepository(db));
  const deletionService = new UserDeletionService(new UserDeletionRepository(db));
  const authorizeAdmin = createAdminAuthorization(appConfig.adminToken);

  app.use(express.json());
  app.use('/api', createCheckoutRoutes(new CheckoutController(checkoutService)));
  app.use('/api', createFinancialReportRoutes(new FinancialReportController(reportService), authorizeAdmin));
  app.use('/api', createUserRoutes(new UserController(deletionService), authorizeAdmin));
  app.use(errorMiddleware);
  app.locals.db = db;
  return app;
}

async function start() {
  const app = await createApp(config);
  const server = app.listen(config.port, () => logger.info('LMS API rodando', { port: config.port }));
  const close = () => server.close(async () => {
    await app.locals.db.close();
    process.exit(0);
  });
  process.once('SIGTERM', close);
  process.once('SIGINT', close);
}

if (require.main === module) {
  start().catch((error) => {
    logger.error('Falha ao iniciar aplicação', { error });
    process.exit(1);
  });
}

module.exports = { createApp };
