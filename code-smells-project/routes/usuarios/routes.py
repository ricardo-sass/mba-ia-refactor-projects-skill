from flask import Blueprint, jsonify, request


def create_blueprint(controller):
    blueprint = Blueprint("usuarios", __name__)

    def respond(result):
        payload, status = result
        return jsonify(payload), status

    @blueprint.get("/usuarios")
    def list_users():
        return respond(controller.list_users())

    @blueprint.get("/usuarios/<int:user_id>")
    def get_user(user_id):
        return respond(controller.get_user(user_id))

    @blueprint.post("/usuarios")
    def create_user():
        return respond(controller.create_user(request.get_json(silent=True)))

    @blueprint.post("/login")
    def login():
        return respond(controller.login(request.get_json(silent=True)))

    return blueprint

