from flask import Blueprint, jsonify, request


def create_blueprint(controller):
    blueprint = Blueprint("catalogo", __name__)

    def respond(result):
        payload, status = result
        return jsonify(payload), status

    @blueprint.get("/produtos")
    def list_products():
        return respond(controller.list_products())

    @blueprint.get("/produtos/busca")
    def search_products():
        return respond(
            controller.search_products(
                request.args.get("q", ""),
                request.args.get("categoria"),
                request.args.get("preco_min"),
                request.args.get("preco_max"),
            )
        )

    @blueprint.get("/produtos/<int:product_id>")
    def get_product(product_id):
        return respond(controller.get_product(product_id))

    @blueprint.post("/produtos")
    def create_product():
        return respond(controller.create_product(request.get_json(silent=True)))

    @blueprint.put("/produtos/<int:product_id>")
    def update_product(product_id):
        return respond(controller.update_product(product_id, request.get_json(silent=True)))

    @blueprint.delete("/produtos/<int:product_id>")
    def delete_product(product_id):
        return respond(controller.delete_product(product_id))

    return blueprint

