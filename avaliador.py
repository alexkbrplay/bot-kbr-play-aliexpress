def calcular_score(p):
    score = 0

    desconto = p.get("discount") or 0
    vendas = p.get("sold_quantity") or 0
    frete = p.get("free_shipping") or False
    origem = str(p.get("ship_from") or "").upper()
    preco = p.get("price") or 0
    tem_preco_original = p.get("original_price") is not None

    # Desconto
    if desconto >= 70:
        score += 35
    elif desconto >= 50:
        score += 25
    elif desconto >= 30:
        score += 15
    elif desconto >= 15:
        score += 10
    elif desconto >= 5:
        score += 5

    # Produto sem preço original
    if not tem_preco_original and preco <= 50:
        score += 10
    elif not tem_preco_original and preco <= 100:
        score += 5

    # Vendas
    if vendas >= 500:
        score += 20
    elif vendas >= 100:
        score += 12
    elif vendas >= 30:
        score += 8
    elif vendas >= 10:
        score += 4

    # Frete grátis
    if frete:
        score += 10

    # Envio do Brasil
    if "BR" in origem:
        score += 30

    # Preço (bônus para produtos baratos)
    if preco <= 50:
        score += 25
    elif preco <= 100:
        score += 15
    elif preco <= 200:
        score += 8
    elif preco <= 350:
        score += 3
    elif preco > 500:
        score -= 10

    return score


def produto_aprovado(p):
    score = int(round(calcular_score(p)))
    desconto = p.get("discount") or 0
    preco = p.get("price") or 0
    tem_preco_original = p.get("original_price") is not None

    # Produto muito caro: só passa com desconto alto
    if preco > 800 and desconto < 60:
        return False

    # Oferta de ouro
    if desconto >= 60:
        return True

    # Score mínimo
    if not tem_preco_original:
        if score >= 30:
            return True
    else:
        if score >= 25:
            return True

    return False