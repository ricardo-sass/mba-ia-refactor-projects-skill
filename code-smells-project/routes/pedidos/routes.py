from flask import Blueprint, jsonify, request


def create_blueprint(controller):
    blueprint = Blueprint("pedidos", __name__)

    def respond(result):
        payload, status = result
        return jsonify(payload), status

    @blueprint.post("/pedidos")
    def create_order():
        return respond(controller.create_order(request.get_json(silent=True)))

    @blueprint.get("/pedidos")
    def list_orders():
        return respond(controller.list_all())

    @blueprint.get("/pedidos/usuario/<int:user_id>")
    def list_orders_by_user(user_id):
        return respond(controller.list_by_user(user_id))

    @blueprint.put("/pedidos/<int:order_id>/status")
    def update_order_status(order_id):
        return respond(controller.update_status(order_id, request.get_json(silent=True)))

    return blueprint

