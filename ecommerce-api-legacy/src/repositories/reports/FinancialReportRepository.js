class FinancialReportRepository {
  constructor(db) { this.db = db; }
  async buildReport() {
    const rows = await this.db.all(`SELECT c.id AS course_id, c.title AS course_title,
      u.name AS user_name, p.amount AS payment_amount, p.status AS payment_status
      FROM courses c
      LEFT JOIN enrollments e ON e.course_id = c.id
      LEFT JOIN users u ON u.id = e.user_id
      LEFT JOIN payments p ON p.enrollment_id = e.id
      ORDER BY c.id, e.id`);
    const byCourse = new Map();
    for (const row of rows) {
      if (!byCourse.has(row.course_id)) byCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
      const course = byCourse.get(row.course_id);
      if (row.user_name || row.payment_amount !== null) {
        if (row.payment_status === 'PAID') course.revenue += row.payment_amount;
        course.students.push({ student: row.user_name || 'Unknown', paid: row.payment_amount || 0 });
      }
    }
    return [...byCourse.values()];
  }
}

module.exports = { FinancialReportRepository };
