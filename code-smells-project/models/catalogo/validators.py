from shared.errors import ValidationError


CATEGORIAS_VALIDAS = {
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
}


def validate_product_payload(data):
    if not isinstance(data, dict):
        raise ValidationError("Dados inválidos")
    if "nome" not in data:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in data:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in data:
        raise ValidationError("Estoque é obrigatório")

    nome = data["nome"]
    descricao = data.get("descricao", "")
    preco = data["preco"]
    estoque = data["estoque"]
    categoria = data.get("categoria", "geral")

    if not isinstance(nome, str) or len(nome) < 2:
        raise ValidationError("Nome muito curto")
    if len(nome) > 200:
        raise ValidationError("Nome muito longo")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição inválida")
    if isinstance(preco, bool) or not isinstance(preco, (int, float)):
        raise ValidationError("Preço inválido")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if isinstance(estoque, bool) or not isinstance(estoque, int):
        raise ValidationError("Estoque inválido")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_VALIDAS)}")

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validate_search_params(term, category, minimum, maximum):
    try:
        minimum = float(minimum) if minimum not in (None, "") else None
        maximum = float(maximum) if maximum not in (None, "") else None
    except (TypeError, ValueError) as error:
        raise ValidationError("Preço inválido") from error
    if minimum is not None and minimum < 0:
        raise ValidationError("Preço mínimo inválido")
    if maximum is not None and maximum < 0:
        raise ValidationError("Preço máximo inválido")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValidationError("Faixa de preço inválida")
    if category and category not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida")
    return str(term or ""), category, minimum, maximum

