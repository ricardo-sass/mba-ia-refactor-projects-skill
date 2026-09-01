from collections import OrderedDict

from shared.errors import ValidationError


VALID_STATUSES = {"pendente", "aprovado", "enviado", "entregue", "cancelado"}
ALLOWED_TRANSITIONS = {
    "pendente": {"aprovado", "cancelado"},
    "aprovado": {"enviado", "cancelado"},
    "enviado": {"entregue"},
    "entregue": set(),
    "cancelado": set(),
}


def validate_order_payload(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    user_id = data.get("usuario_id")
    items = data.get("itens")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError("Usuario ID é obrigatório")
    if not isinstance(items, list) or not items:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    aggregated = OrderedDict()
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError("Item inválido")
        product_id = item.get("produto_id")
        quantity = item.get("quantidade")
        if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
            raise ValidationError("Produto inválido")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValidationError("Quantidade deve ser positiva")
        aggregated[product_id] = aggregated.get(product_id, 0) + quantity

    return user_id, [
        {"produto_id": product_id, "quantidade": quantity}
        for product_id, quantity in aggregated.items()
    ]


def validate_status_payload(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    status = data.get("status", "")
    if status not in VALID_STATUSES:
        raise ValidationError("Status inválido")
    return status

