def filtrar_produto(p):
    titulo = str(p.get("title") or "").lower()
    preco = p.get("price") or 0

    # Cadeiras muito caras
    if "chair" in titulo and preco > 500:
        print(f"   [BLOQUEADO] Cadeira muito cara: R${preco}")
        return False

    # Produtos usados
    if "used" in titulo:
        print(f"   [BLOQUEADO] Produto usado")
        return False

    # Peças genéricas
    if "contact customer service" in titulo or "send the" in titulo:
        print(f"   [BLOQUEADO] Peça genérica")
        return False

    if "model number" in titulo or "model:" in titulo:
        print(f"   [BLOQUEADO] Peça com modelo")
        return False

    # Capas de celular
    if "case" in titulo or "capa" in titulo:
        print(f"   [BLOQUEADO] Capa de celular")
        return False

    # Lista de palavras de reposição
    palavras_reposicao = [
        "replacement", "replace", "reparo", "peça", "peças", "conserto",
        "spare", "part", "parts", "battery", "bateria", "cabo", "cable",
        "adapter", "adaptador", "splitter", "conversor", "remote",
        "controle", "remoto", "foam", "ear pads", "earpads", "memory foam",
        "almofada", "espuma", "ponteira", "headband", "microfone",
        "placa", "board", "mainboard", "controladora", "earmuffs",
    ]

    for palavra in palavras_reposicao:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Peça/reposição: '{palavra}'")
            return False

    # Preço muito baixo
    if preco < 15:
        print(f"   [BLOQUEADO] Preço muito baixo: R${preco}")
        return False

    # Marcas caras com preço suspeito
    marcas_sensiveis = [
        "apple", "iphone", "samsung", "xiaomi", "motorola"
    ]

    for marca in marcas_sensiveis:
        if marca in titulo and preco < 50:
            print(f"   [BLOQUEADO] {marca.upper()} a R${preco} — preço suspeito")
            return False

    return True