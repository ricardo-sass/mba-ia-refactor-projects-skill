from models.usuarios.validators import validate_login_payload, validate_user_payload
from shared.errors import AuthenticationError, NotFoundError


class UserController:
    def __init__(self, model, service):
        self.model = model
        self.service = service

    def list_users(self):
        return {"dados": self.model.list_all(), "sucesso": True}, 200

    def get_user(self, user_id):
        user = self.model.find_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado")
        return {"dados": user, "sucesso": True}, 200

    def create_user(self, data):
        user = validate_user_payload(data)
        user_id = self.service.create(user)
        return {"dados": {"id": user_id}, "sucesso": True}, 201

    def login(self, data):
        email, password = validate_login_payload(data)
        user = self.service.authenticate(email, password)
        if user is None:
            raise AuthenticationError("Email ou senha inválidos")
        return {"dados": user, "sucesso": True, "mensagem": "Login OK"}, 200

