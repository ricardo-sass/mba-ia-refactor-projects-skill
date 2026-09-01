from flask import Blueprint, jsonify


def create_report_blueprint(controller, auth_middleware) -> Blueprint:
    blueprint = Blueprint("reports", __name__)
    managers = auth_middleware.required(("admin", "manager"))

    @blueprint.get("/reports/summary")
    @managers
    def summary_report():
        return jsonify(controller.summary()), 200

    @blueprint.get("/reports/user/<int:user_id>")
    @managers
    def user_report(user_id: int):
        return jsonify(controller.user(user_id)), 200

    return blueprint
