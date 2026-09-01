class HealthRepository:
    def __init__(self, connection_provider):
        self.connection_provider = connection_provider

    def snapshot(self):
        connection = self.connection_provider()
        connection.execute("SELECT 1")
        return {
            "produtos": connection.execute("SELECT COUNT(*) FROM produtos").fetchone()[0],
            "usuarios": connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
            "pedidos": connection.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
        }

