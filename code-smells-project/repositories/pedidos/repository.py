from shared.errors import NotFoundError, ValidationError


class OrderRepository:
    def __init__(self, connection_provider):
        self.connection_provider = connection_provider

    def create(self, user_id, items):
        connection = self.connection_provider()
        if connection.execute("SELECT 1 FROM usuarios WHERE id = ?", (user_id,)).fetchone() is None:
            raise ValidationError("Usuário não encontrado")

        product_ids = [item["produto_id"] for item in items]
        placeholders = ", ".join("?" for _ in product_ids)
        rows = connection.execute(
            f"SELECT id, nome, preco, estoque FROM produtos WHERE id IN ({placeholders})",
            product_ids,
        ).fetchall()
        products = {row["id"]: row for row in rows}

        total = 0
        for item in items:
            product = products.get(item["produto_id"])
            if product is None:
                raise ValidationError(f"Produto {item['produto_id']} não encontrado")
            if product["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {product['nome']}")
            total += product["preco"] * item["quantidade"]

        try:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                    (user_id, "pendente", total),
                )
                order_id = cursor.lastrowid
                for item in items:
                    product = products[item["produto_id"]]
                    connection.execute(
                        """
                        INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
                        VALUES (?, ?, ?, ?)
                        """,
                        (order_id, product["id"], item["quantidade"], product["preco"]),
                    )
                    updated = connection.execute(
                        """
                        UPDATE produtos SET estoque = estoque - ?
                        WHERE id = ? AND estoque >= ?
                        """,
                        (item["quantidade"], product["id"], item["quantidade"]),
                    )
                    if updated.rowcount != 1:
                        raise ValidationError(f"Estoque insuficiente para {product['nome']}")
        except Exception:
            connection.rollback()
            raise
        return {"pedido_id": order_id, "total": total}

    def list_by_user(self, user_id):
        return self._list("WHERE p.usuario_id = ?", (user_id,))

    def list_all(self):
        return self._list()

    def _list(self, where_clause="", parameters=()):
        rows = self.connection_provider().execute(
            f"""
            SELECT
                p.id AS pedido_id,
                p.usuario_id,
                p.status,
                p.total,
                p.criado_em,
                i.produto_id,
                i.quantidade,
                i.preco_unitario,
                pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido i ON i.pedido_id = p.id
            LEFT JOIN produtos pr ON pr.id = i.produto_id
            {where_clause}
            ORDER BY p.id, i.id
            """,
            parameters,
        ).fetchall()

        orders = {}
        for row in rows:
            order = orders.setdefault(
                row["pedido_id"],
                {
                    "id": row["pedido_id"],
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": [],
                },
            )
            if row["produto_id"] is not None:
                order["itens"].append(
                    {
                        "produto_id": row["produto_id"],
                        "produto_nome": row["produto_nome"] or "Desconhecido",
                        "quantidade": row["quantidade"],
                        "preco_unitario": row["preco_unitario"],
                    }
                )
        return list(orders.values())

    def find_status(self, order_id):
        row = self.connection_provider().execute(
            "SELECT status FROM pedidos WHERE id = ?", (order_id,)
        ).fetchone()
        return row["status"] if row else None

    def update_status(self, order_id, current_status, new_status):
        connection = self.connection_provider()
        try:
            with connection:
                if new_status == "cancelado":
                    items = connection.execute(
                        "SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?",
                        (order_id,),
                    ).fetchall()
                    for item in items:
                        connection.execute(
                            "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
                            (item["quantidade"], item["produto_id"]),
                        )
                updated = connection.execute(
                    "UPDATE pedidos SET status = ? WHERE id = ? AND status = ?",
                    (new_status, order_id, current_status),
                )
                if updated.rowcount != 1:
                    raise NotFoundError("Pedido não encontrado")
        except Exception:
            connection.rollback()
            raise

