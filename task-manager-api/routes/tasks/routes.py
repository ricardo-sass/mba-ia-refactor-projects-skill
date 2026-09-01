from flask import Blueprint, jsonify, request


def create_task_blueprint(controller, auth_middleware) -> Blueprint:
    blueprint = Blueprint("tasks", __name__)
    authenticated = auth_middleware.required(("user", "admin", "manager"))

    @blueprint.get("/tasks")
    @authenticated
    def get_tasks():
        return jsonify(controller.list()), 200

    @blueprint.get("/tasks/<int:task_id>")
    @authenticated
    def get_task(task_id: int):
        return jsonify(controller.get(task_id)), 200

    @blueprint.post("/tasks")
    @authenticated
    def create_task():
        return jsonify(controller.create(request.get_json(silent=True))), 201

    @blueprint.put("/tasks/<int:task_id>")
    @authenticated
    def update_task(task_id: int):
        return jsonify(controller.update(task_id, request.get_json(silent=True))), 200

    @blueprint.delete("/tasks/<int:task_id>")
    @authenticated
    def delete_task(task_id: int):
        return jsonify(controller.delete(task_id)), 200

    @blueprint.get("/tasks/search")
    @authenticated
    def search_tasks():
        return jsonify(controller.search(request.args.to_dict())), 200

    @blueprint.get("/tasks/stats")
    @authenticated
    def task_stats():
        return jsonify(controller.statistics()), 200

    return blueprint
