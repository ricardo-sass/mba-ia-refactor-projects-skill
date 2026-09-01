const config = {
  port: Number(process.env.PORT || 3000),
  adminToken: process.env.ADMIN_TOKEN,
  database: { filename: process.env.SQLITE_FILENAME || ':memory:' }
};

module.exports = { config };
