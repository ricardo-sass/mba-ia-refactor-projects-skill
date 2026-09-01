from flask import Blueprint, jsonify


def create_blueprint(controller):
    blueprint = Blueprint("relatorios", __name__)

    @blueprint.get("/relatorios/vendas")
    def sales_report():
        payload, status = controller.sales_report()
        return jsonify(payload), status

    return blueprint

