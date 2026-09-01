class UserRepository {
  constructor(db) { this.db = db; }
  findByEmail(email) { return this.db.get('SELECT id FROM users WHERE email = ?', [email]); }
  create(user, tx) {
    return tx.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [user.name, user.email, user.passwordHash]);
  }
}

module.exports = { UserRepository };
