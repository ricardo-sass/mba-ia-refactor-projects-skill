class OperationalController:
    def __init__(self, health_repository, environment):
        self.health_repository = health_repository
        self.environment = environment

    def index(self):
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }, 200

    def health(self):
        return {
            "status": "ok",
            "database": "connected",
            "counts": self.health_repository.snapshot(),
            "versao": "1.0.0",
            "ambiente": self.environment,
        }, 200

