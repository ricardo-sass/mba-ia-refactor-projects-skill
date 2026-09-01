from werkzeug.security import check_password_hash, generate_password_hash

from models.usuarios.model import serialize_user


HASH_PREFIXES = ("scrypt:", "pbkdf2:", "argon2:")


class UserService:
    def __init__(self, user_model):
        self.user_model = user_model

    def create(self, user):
        password_hash = generate_password_hash(user["senha"])
        return self.user_model.create(user["nome"], user["email"], password_hash)

    def authenticate(self, email, password):
        row = self.user_model.find_for_authentication(email)
        if row is None:
            return None

        stored_password = row["senha"]
        if stored_password.startswith(HASH_PREFIXES):
            valid = check_password_hash(stored_password, password)
        else:
            valid = stored_password == password
            if valid:
                self.user_model.update_password_hash(row["id"], generate_password_hash(password))

        return serialize_user(row) if valid else None

