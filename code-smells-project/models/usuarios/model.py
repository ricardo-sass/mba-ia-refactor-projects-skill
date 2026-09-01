import sqlite3

from shared.errors import ConflictError


def serialize_user(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


class UserModel:
    def __init__(self, connection_provider):
        self.connection_provider = connection_provider

    def list_all(self):
        rows = self.connection_provider().execute(
            "SELECT id, nome, email, tipo, criado_em FROM usuarios"
        ).fetchall()
        return [serialize_user(row) for row in rows]

    def find_by_id(self, user_id):
        row = self.connection_provider().execute(
            "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (user_id,)
        ).fetchone()
        return serialize_user(row) if row else None

    def find_for_authentication(self, email):
        return self.connection_provider().execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()

    def create(self, name, email, password_hash, user_type="cliente"):
        connection = self.connection_provider()
        if connection.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,)).fetchone():
            raise ConflictError("Email já cadastrado")
        try:
            cursor = connection.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (name, email, password_hash, user_type),
            )
            connection.commit()
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ConflictError("Email já cadastrado") from error
        return cursor.lastrowid

    def update_password_hash(self, user_id, password_hash):
        connection = self.connection_provider()
        connection.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (password_hash, user_id))
        connection.commit()
