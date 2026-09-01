from shared.errors import ValidationError


def validate_user_payload(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    nome = data.get("nome", "")
    email = data.get("email", "")
    senha = data.get("senha", "")
    if not all(isinstance(value, str) and value for value in (nome, email, senha)):
        raise ValidationError("Nome, email e senha são obrigatórios")
    if "@" not in email or len(email) > 254:
        raise ValidationError("Email inválido")
    if len(senha) < 6:
        raise ValidationError("Senha deve ter pelo menos 6 caracteres")
    return {"nome": nome, "email": email.lower(), "senha": senha}


def validate_login_payload(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    email = data.get("email", "")
    senha = data.get("senha", "")
    if not isinstance(email, str) or not isinstance(senha, str) or not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    return email.lower(), senha

