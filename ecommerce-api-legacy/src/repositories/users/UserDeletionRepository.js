class UserDeletionRepository {
  constructor(db) { this.db = db; }
  transaction(work) { return this.db.transaction(work); }
  deleteUserById(userId, tx) { return tx.run('DELETE FROM users WHERE id = ?', [userId]); }
}

module.exports = { UserDeletionRepository };
