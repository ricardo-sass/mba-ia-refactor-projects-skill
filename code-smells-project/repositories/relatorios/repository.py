class SalesReportRepository:
    def __init__(self, connection_provider):
        self.connection_provider = connection_provider

    def sales_totals(self):
        row = self.connection_provider().execute(
            """
            SELECT
                COUNT(*) AS total_pedidos,
                COALESCE(SUM(total), 0) AS faturamento,
                SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
                SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados,
                SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
            FROM pedidos
            """
        ).fetchone()
        return dict(row)

