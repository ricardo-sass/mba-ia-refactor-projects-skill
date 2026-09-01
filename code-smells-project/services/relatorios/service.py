from models.relatorios import calculate_discount


class SalesReportService:
    def __init__(self, repository):
        self.repository = repository

    def build(self):
        totals = self.repository.sales_totals()
        revenue = totals["faturamento"]
        discount = calculate_discount(revenue)

        order_count = totals["total_pedidos"]
        return {
            "total_pedidos": order_count,
            "faturamento_bruto": round(revenue, 2),
            "desconto_aplicavel": round(discount, 2),
            "faturamento_liquido": round(revenue - discount, 2),
            "pedidos_pendentes": totals["pendentes"],
            "pedidos_aprovados": totals["aprovados"],
            "pedidos_cancelados": totals["cancelados"],
            "ticket_medio": round(revenue / order_count, 2) if order_count else 0,
        }
