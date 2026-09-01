const sqlite3 = require('sqlite3').verbose();

function createSqliteDatabase(filename) {
  const connection = new sqlite3.Database(filename);
  const run = (sql, params = []) => new Promise((resolve, reject) => {
    connection.run(sql, params, function complete(err) {
      if (err) return reject(err);
      return resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
  const get = (sql, params = []) => new Promise((resolve, reject) => {
    connection.get(sql, params, (err, row) => err ? reject(err) : resolve(row));
  });
  const all = (sql, params = []) => new Promise((resolve, reject) => {
    connection.all(sql, params, (err, rows) => err ? reject(err) : resolve(rows));
  });
  const transaction = async (work) => {
    await run('BEGIN');
    try {
      const result = await work({ run, get, all });
      await run('COMMIT');
      return result;
    } catch (error) {
      await run('ROLLBACK');
      throw error;
    }
  };
  const close = () => new Promise((resolve, reject) => {
    connection.close((err) => err ? reject(err) : resolve());
  });
  return { run, get, all, transaction, close };
}

module.exports = { createSqliteDatabase };
