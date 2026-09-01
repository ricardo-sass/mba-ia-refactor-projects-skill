from flask import Blueprint, jsonify


def create_blueprint(controller):
    blueprint = Blueprint("operacional", __name__)

    def respond(result):
        payload, status = result
        return jsonify(payload), status

    @blueprint.get("/")
    def index():
        return respond(controller.index())

    @blueprint.get("/health")
    def health():
        return respond(controller.health())

    return blueprint

