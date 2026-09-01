from models.pedidos.validators import validate_order_payload, validate_status_payload


class OrderController:
    def __init__(self, repository, service):
        self.repository = repository
        self.service = service

    def create_order(self, data):
        user_id, items = validate_order_payload(data)
        result = self.service.create(user_id, items)
        return {
            "dados": result,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }, 201

    def list_by_user(self, user_id):
        return {"dados": self.repository.list_by_user(user_id), "sucesso": True}, 200

    def list_all(self):
        return {"dados": self.repository.list_all(), "sucesso": True}, 200

    def update_status(self, order_id, data):
        new_status = validate_status_payload(data)
        self.service.update_status(order_id, new_status)
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200

