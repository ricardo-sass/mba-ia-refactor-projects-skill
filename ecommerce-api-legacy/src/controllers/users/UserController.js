class UserController {
  constructor(service) { this.service = service; }
  deleteUser(id) { return this.service.deleteUser(id); }
}

module.exports = { UserController };
