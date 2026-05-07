def filtrar_produto(p):
    titulo = str(p.get("title") or "").lower()
    preco = p.get("price") or 0

    # Cadeiras muito caras
    if "chair" in titulo and preco > 500:
        return False

    # Produtos usados
    if "used" in titulo:
        return False

    # ==========================================
    # NOVAS REGRAS PARA BLOQUEAR "LIXO"
    # ==========================================

    # Conversores / adaptadores de voltagem
    palavras_conversor = [
        "dc-dc", "dc dc", "conversor", "converter", "step down", "buck",
        "voltage", "alimentação", "36v", "24v", "12v", "5v", "9v"
    ]
    for palavra in palavras_conversor:
        if palavra in titulo and ("charger" not in titulo and "carregador" not in titulo):
            print(f"   [BLOQUEADO] Conversor: {palavra}")
            return False

    # Fitas adesivas / grip tape
    palavras_fita = ["grip tape", "mouse tape", "adesivo", "sticker", "fita", "antiderrapante"]
    for palavra in palavras_fita:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Fita adesiva: {palavra}")
            return False

    # Ventoinhas / coolers (peças)
    palavras_fan = ["cooler fan", "ventilador", "fan for", "gpu fan", "vga fan", "placa gráfica"]
    for palavra in palavras_fan:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Ventoinha: {palavra}")
            return False

    # Lâmpadas / iluminação
    palavras_lamp = ["lamp", "bulb", "led", "e27", "lâmpada", "iluminação", "emergency light"]
    for palavra in palavras_lamp:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Lâmpada: {palavra}")
            return False

    # Tomadas / smart home (fora do foco)
    palavras_tomada = ["tomada", "socket", "wall outlet", "power monitor", "tuya", "smart home"]
    for palavra in palavras_tomada:
        if palavra in titulo and "power supply" not in titulo:
            print(f"   [BLOQUEADO] Tomada/Smart: {palavra}")
            return False

    # Testadores / ferramentas de diagnóstico
    palavras_teste = ["testador", "tester", "diagnóstico", "diagnostic", "ferramenta"]
    for palavra in palavras_teste:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Testador: {palavra}")
            return False

    # Pontas de silicone / almofadas para fone
    palavras_ponteira = ["ear tip", "ear tip", "silicone tip", "almofada", "ear cushion", "kutou"]
    for palavra in palavras_ponteira:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Ponteira: {palavra}")
            return False

    # Motores pequenos / peças minúsculas
    palavras_motor = ["motor", "coreless", "mini motor", "0308", "relógio inteligente"]
    for palavra in palavras_motor:
        if palavra in titulo and "smartwatch" not in titulo:
            print(f"   [BLOQUEADO] Motor/peça: {palavra}")
            return False

    # Suportes de HD / baias
    palavras_suporte = ["bay", "rack móvel", "hot swap", "backplane", "2.5 polegada", "3.5 polegada"]
    for palavra in palavras_suporte:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Suporte HD: {palavra}")
            return False

    # Códigos genéricos (peças)
    import re
    if re.search(r'pld\d{5}', titulo) or re.search(r't\d{6}', titulo) or re.search(r'ga\d{2}s', titulo):
        print(f"   [BLOQUEADO] Código genérico de peça")
        return False

    # Produtos de bike (não é hardware PC)
    palavras_bike = ["bicicleta", "bike", "bicycle", "guidão", "extensão superior"]
    for palavra in palavras_bike:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Produto de bike: {palavra}")
            return False

    # Stickers / selos / embalagem
    palavras_sticker = ["sticker", "selo", "embalagem", "wrapping", "caixa de vedação", "etiqueta"]
    for palavra in palavras_sticker:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Sticker/embalagem: {palavra}")
            return False

    # ==========================================
    # REGRAS EXISTENTES (mantidas)
    # ==========================================

    # Capas de celular
    if "case" in titulo and "airpods" not in titulo:
        print(f"   [BLOQUEADO] Capa de celular")
        return False

    # Preço muito baixo
    if preco < 15:
        print(f"   [BLOQUEADO] Preço muito baixo: R${preco}")
        return False

    return True