class CourseRepository {
  constructor(db) { this.db = db; }
  findActiveById(courseId) {
    return this.db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [courseId]);
  }
}

module.exports = { CourseRepository };
