from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from shared.errors import AppError


class AuthService:
    def __init__(self, repository, secret_key: str, max_age: int = 3600) -> None:
        self.repository = repository
        self.serializer = URLSafeTimedSerializer(secret_key, salt="task-manager-auth")
        self.max_age = max_age

    def login(self, email: str | None, password: str | None) -> tuple[dict, str]:
        if not email or not password:
            raise AppError("Email e senha são obrigatórios", 400)
        if not isinstance(email, str) or not isinstance(password, str):
            raise AppError("Dados inválidos", 400)

        user = self.repository.find_by_email(email)
        if not user or not user.check_password(password):
            raise AppError("Credenciais inválidas", 401)
        if not user.active:
            raise AppError("Usuário inativo", 403)

        if user.has_legacy_password:
            user.set_password(password)
            self.repository.commit()

        token = self.serializer.dumps({"user_id": user.id, "role": user.role})
        return user.to_dict(), token

    def verify_token(self, token: str):
        try:
            payload = self.serializer.loads(token, max_age=self.max_age)
        except SignatureExpired:
            raise AppError("Token expirado", 401)
        except BadSignature:
            raise AppError("Token inválido", 401)

        user = self.repository.find_by_id(payload.get("user_id"))
        if not user or not user.active:
            raise AppError("Token inválido", 401)
        return user
