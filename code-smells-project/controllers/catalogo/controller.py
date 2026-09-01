from models.catalogo.validators import validate_product_payload, validate_search_params
from shared.errors import NotFoundError


class CatalogController:
    def __init__(self, model):
        self.model = model

    def list_products(self):
        return {"dados": self.model.list_all(), "sucesso": True}, 200

    def get_product(self, product_id):
        product = self.model.find_by_id(product_id)
        if product is None:
            raise NotFoundError("Produto não encontrado")
        return {"dados": product, "sucesso": True}, 200

    def create_product(self, data):
        product = validate_product_payload(data)
        product_id = self.model.create(product)
        return {"dados": {"id": product_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    def update_product(self, product_id, data):
        if self.model.find_by_id(product_id) is None:
            raise NotFoundError("Produto não encontrado")
        product = validate_product_payload(data)
        self.model.update(product_id, product)
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def delete_product(self, product_id):
        if self.model.find_by_id(product_id) is None:
            raise NotFoundError("Produto não encontrado")
        self.model.delete(product_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200

    def search_products(self, term, category, minimum, maximum):
        params = validate_search_params(term, category, minimum, maximum)
        products = self.model.search(*params)
        return {"dados": products, "total": len(products), "sucesso": True}, 200

