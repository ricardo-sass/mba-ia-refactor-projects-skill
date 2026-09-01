class CheckoutRepository {
  constructor(db) { this.db = db; }
  transaction(work) { return this.db.transaction(work); }
  createEnrollment(userId, courseId, tx) {
    return tx.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
  }
  createPayment(enrollmentId, amount, status, tx) {
    return tx.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
  }
  createAuditLog(action, tx) {
    return tx.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);
  }
}

module.exports = { CheckoutRepository };
