from flask import Blueprint, g, jsonify, request


def create_user_blueprint(controller, auth_middleware) -> Blueprint:
    blueprint = Blueprint("users", __name__)
    authenticated = auth_middleware.required()
    admin_only = auth_middleware.required(("admin",))

    @blueprint.get("/users")
    @authenticated
    def get_users():
        return jsonify(controller.list()), 200

    @blueprint.get("/users/<int:user_id>")
    @authenticated
    def get_user(user_id: int):
        return jsonify(controller.get(user_id)), 200

    @blueprint.post("/users")
    @admin_only
    def create_user():
        return jsonify(controller.create(request.get_json(silent=True))), 201

    @blueprint.put("/users/<int:user_id>")
    @authenticated
    def update_user(user_id: int):
        return jsonify(
            controller.update(user_id, request.get_json(silent=True), g.current_user)
        ), 200

    @blueprint.delete("/users/<int:user_id>")
    @admin_only
    def delete_user(user_id: int):
        return jsonify(controller.delete(user_id)), 200

    @blueprint.get("/users/<int:user_id>/tasks")
    @authenticated
    def get_user_tasks(user_id: int):
        return jsonify(controller.tasks(user_id)), 200

    @blueprint.post("/login")
    def login():
        return jsonify(controller.login(request.get_json(silent=True))), 200

    return blueprint
