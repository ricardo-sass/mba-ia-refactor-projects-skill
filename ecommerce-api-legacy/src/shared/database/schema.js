const { hashPassword } = require('../../models/users/passwordHash');

async function initializeDatabase(db) {
  await db.run('PRAGMA foreign_keys = ON');
  await db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL)');
  await db.run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL)');
  await db.run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(course_id) REFERENCES courses(id))');
  await db.run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL, amount REAL NOT NULL, status TEXT NOT NULL, FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE)');
  await db.run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
  await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', hashPassword('seed-test-password')]);
  await db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
  await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
  await db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
}

module.exports = { initializeDatabase };
