from flask import Blueprint, jsonify, request


def create_category_blueprint(controller, auth_middleware) -> Blueprint:
    blueprint = Blueprint("categories", __name__)
    authenticated = auth_middleware.required()
    managers = auth_middleware.required(("admin", "manager"))

    @blueprint.get("/categories")
    @authenticated
    def get_categories():
        return jsonify(controller.list()), 200

    @blueprint.post("/categories")
    @managers
    def create_category():
        return jsonify(controller.create(request.get_json(silent=True))), 201

    @blueprint.put("/categories/<int:category_id>")
    @managers
    def update_category(category_id: int):
        return jsonify(
            controller.update(category_id, request.get_json(silent=True))
        ), 200

    @blueprint.delete("/categories/<int:category_id>")
    @managers
    def delete_category(category_id: int):
        return jsonify(controller.delete(category_id)), 200

    return blueprint
