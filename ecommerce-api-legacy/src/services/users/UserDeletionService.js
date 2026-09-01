class UserDeletionService {
  constructor(repository) { this.repository = repository; }
  async deleteUser(userId) {
    await this.repository.transaction((tx) => this.repository.deleteUserById(userId, tx));
    return 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';
  }
}

module.exports = { UserDeletionService };
