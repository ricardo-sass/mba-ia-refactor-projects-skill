import logging

from models.pedidos.validators import ALLOWED_TRANSITIONS
from shared.errors import NotFoundError, ValidationError


class OrderService:
    def __init__(self, repository, logger=None):
        self.repository = repository
        self.logger = logger or logging.getLogger(__name__)

    def create(self, user_id, items):
        result = self.repository.create(user_id, items)
        self.logger.info("Pedido criado", extra={"pedido_id": result["pedido_id"], "usuario_id": user_id})
        return result

    def update_status(self, order_id, new_status):
        current_status = self.repository.find_status(order_id)
        if current_status is None:
            raise NotFoundError("Pedido não encontrado")
        if new_status not in ALLOWED_TRANSITIONS[current_status]:
            raise ValidationError("Transição de status inválida")

        self.repository.update_status(order_id, current_status, new_status)
        self.logger.info(
            "Status do pedido atualizado",
            extra={"pedido_id": order_id, "status_anterior": current_status, "novo_status": new_status},
        )

