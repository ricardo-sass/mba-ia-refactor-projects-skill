from shared.errors import ConflictError


def serialize_product(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


class CatalogModel:
    def __init__(self, connection_provider):
        self.connection_provider = connection_provider

    def list_all(self):
        rows = self.connection_provider().execute("SELECT * FROM produtos").fetchall()
        return [serialize_product(row) for row in rows]

    def find_by_id(self, product_id):
        row = self.connection_provider().execute(
            "SELECT * FROM produtos WHERE id = ?", (product_id,)
        ).fetchone()
        return serialize_product(row) if row else None

    def create(self, product):
        connection = self.connection_provider()
        cursor = connection.execute(
            """
            INSERT INTO produtos (nome, descricao, preco, estoque, categoria)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                product["nome"],
                product["descricao"],
                product["preco"],
                product["estoque"],
                product["categoria"],
            ),
        )
        connection.commit()
        return cursor.lastrowid

    def update(self, product_id, product):
        connection = self.connection_provider()
        connection.execute(
            """
            UPDATE produtos
            SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
            WHERE id = ?
            """,
            (
                product["nome"],
                product["descricao"],
                product["preco"],
                product["estoque"],
                product["categoria"],
                product_id,
            ),
        )
        connection.commit()

    def delete(self, product_id):
        connection = self.connection_provider()
        referenced = connection.execute(
            "SELECT 1 FROM itens_pedido WHERE produto_id = ? LIMIT 1", (product_id,)
        ).fetchone()
        if referenced:
            raise ConflictError("Produto possui pedidos associados")
        connection.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        connection.commit()

    def search(self, term, category=None, minimum=None, maximum=None):
        clauses = ["1 = 1"]
        parameters = []
        if term:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            wildcard = f"%{term}%"
            parameters.extend([wildcard, wildcard])
        if category:
            clauses.append("categoria = ?")
            parameters.append(category)
        if minimum is not None:
            clauses.append("preco >= ?")
            parameters.append(minimum)
        if maximum is not None:
            clauses.append("preco <= ?")
            parameters.append(maximum)

        query = f"SELECT * FROM produtos WHERE {' AND '.join(clauses)}"
        rows = self.connection_provider().execute(query, parameters).fetchall()
        return [serialize_product(row) for row in rows]

