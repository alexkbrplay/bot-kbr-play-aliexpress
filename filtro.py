import re

def filtrar_produto(p):
    titulo = str(p.get("title") or "").lower()
    preco = p.get("price") or 0

    # ==========================================
    # BLOCO 1: AUTOMOTIVO, BICICLETA, CONVERSORES
    # ==========================================
    
    # Produtos automotivos
    palavras_carro = [
        "carro", "automotivo", "veiculo", "tapete", "painel", "volante", 
        "isofix", "parabrisa", "shade", "dashboard mat", "bank socket", 
        "cinto de segurança", "air conditioning", "ventilação"
    ]
    for palavra in palavras_carro:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Produto automotivo: {palavra}")
            return False

    # Bicicleta
    palavras_bike = ["bicicleta", "bike", "bicycle", "guidão", "suporte de bike", "extensão superior", "handlebar"]
    for palavra in palavras_bike:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Produto de bike: {palavra}")
            return False

    # Conversores DC-DC
    palavras_conversor = [
        "dc-dc", "dc dc", "conversor", "converter", "step down", "buck",
        "boost", "36v", "24v", "12v", "5v", "9v", "voltage regulator"
    ]
    for palavra in palavras_conversor:
        if palavra in titulo and ("charger" not in titulo and "carregador" not in titulo):
            print(f"   [BLOQUEADO] Conversor: {palavra}")
            return False

    # ==========================================
    # BLOCO 2: ILUMINAÇÃO, TOMADAS, SMART HOME
    # ==========================================

    # Lâmpadas e iluminação
    palavras_lamp = ["lamp", "bulb", "led", "e27", "lâmpada", "iluminação", "emergency light", "led strip", "fita de led"]
    for palavra in palavras_lamp:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Lâmpada/iluminação: {palavra}")
            return False

    # Tomadas e smart home
    palavras_tomada = ["tomada", "socket", "wall outlet", "power monitor", "tuya", "smart home", "interruptor"]
    for palavra in palavras_tomada:
        if palavra in titulo and "power supply" not in titulo:
            print(f"   [BLOQUEADO] Tomada/smart home: {palavra}")
            return False

    # ==========================================
    # BLOCO 3: FERRAMENTAS E TESTADORES
    # ==========================================

    palavras_teste = ["testador", "tester", "diagnóstico", "diagnostic", "ferramenta", "multímetro", "multimeter"]
    for palavra in palavras_teste:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Testador/ferramenta: {palavra}")
            return False

    # ==========================================
    # BLOCO 4: PEÇAS PEQUENAS, MOTORES, VENTOINHAS
    # ==========================================

    palavras_pecas = ["screw", "parafuso", "connector", "conector", "motor", "coreless", "bearing"]
    for palavra in palavras_pecas:
        if palavra in titulo and ("mouse" not in titulo and "teclado" not in titulo):
            print(f"   [BLOQUEADO] Peça pequena: {palavra}")
            return False

    palavras_fan = ["cooler fan", "ventilador", "fan for", "gpu fan", "vga fan", "placa gráfica", "heatsink"]
    for palavra in palavras_fan:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Ventoinha: {palavra}")
            return False

    # ==========================================
    # BLOCO 5: FITAS, ADESIVOS, STICKERS
    # ==========================================

    palavras_fita = ["grip tape", "mouse tape", "adesivo", "sticker", "fita", "antiderrapante"]
    for palavra in palavras_fita:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Fita/adesivo: {palavra}")
            return False

    palavras_sticker = ["sticker", "selo", "embalagem", "etiqueta", "wrapping", "caixa de vedação"]
    for palavra in palavras_sticker:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Sticker/embalagem: {palavra}")
            return False

    # ==========================================
    # BLOCO 6: PONTEIRAS E ALMOFADAS DE FONE
    # ==========================================

    palavras_ponteira = ["ear tip", "silicone tip", "almofada", "ear cushion", "earmuff", "kutou"]
    for palavra in palavras_ponteira:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Ponteira/almofada: {palavra}")
            return False

    # ==========================================
    # BLOCO 7: SUPORTES, ADAPTADORES, BAIAS
    # ==========================================

    palavras_suporte = ["bay", "rack móvel", "hot swap", "backplane", "adapter", "adaptador", "suporte", "bracket"]
    for palavra in palavras_suporte:
        if palavra in titulo and ("ssd" not in titulo and "hd" not in titulo):
            print(f"   [BLOQUEADO] Suporte/adaptador: {palavra}")
            return False

    # ==========================================
    # BLOCO 8: SMARTWATCH GENÉRICO (PREÇO BAIXO)
    # ==========================================

    if ("smartwatch" in titulo or "smart watch" in titulo or "fitness tracker" in titulo or "smart bracelet" in titulo) and preco < 100:
        if "garmin" not in titulo and "apple" not in titulo and "samsung" not in titulo:
            print(f"   [BLOQUEADO] Smartwatch genérico barato: R${preco}")
            return False

    # ==========================================
    # BLOCO 9: CABOS, CONTROLES, PELÍCULAS, CAPAS
    # ==========================================

    # Cabos (reforço)
    if "cable" in titulo or "cabo" in titulo:
        print(f"   [BLOQUEADO] Cabo: {palavra}")
        return False

    # Controles remoto
    if "remote" in titulo or "controle remoto" in titulo:
        print(f"   [BLOQUEADO] Controle remoto")
        return False

    # Películas e vidros
    palavras_pelicula = ["screen protector", "tempered glass", "película", "vidro"]
    for palavra in palavras_pelicula:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Película/vidro: {palavra}")
            return False

    # Capas de notebook
    if "laptop case" in titulo or "notebook case" in titulo or "capa para notebook" in titulo:
        print(f"   [BLOQUEADO] Capa de notebook")
        return False

    # Suporte de celular
    palavras_holder = ["phone holder", "suporte celular", "car holder"]
    for palavra in palavras_holder:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Suporte de celular: {palavra}")
            return False

    # ==========================================
    # BLOCO 10: PREÇO MUITO BAIXO
    # ==========================================

    if preco < 20:
        print(f"   [BLOQUEADO] Preço muito baixo: R${preco}")
        return False

    # ==========================================
    # CÓDIGOS GENÉRICOS DE PEÇA
    # ==========================================

    if re.search(r'pld\d{5}', titulo) or re.search(r't\d{6}', titulo) or re.search(r'ga\d{2}s', titulo):
        print(f"   [BLOQUEADO] Código genérico de peça")
        return False

    # ==========================================
    # REGRAS LEGADAS (MANTIDAS)
    # ==========================================

    # Capas de celular
    if "case" in titulo and "airpods" not in titulo:
        print(f"   [BLOQUEADO] Capa de celular")
        return False

    # Produtos usados
    if "used" in titulo:
        print(f"   [BLOQUEADO] Produto usado")
        return False

    # Cadeiras muito caras (acima de R$500)
    if "chair" in titulo and preco > 500:
        print(f"   [BLOQUEADO] Cadeira muito cara: R${preco}")
        return False

    # Marcas caras com preço suspeito
    marcas_sensiveis = ["apple", "iphone", "samsung", "xiaomi", "motorola"]
    for marca in marcas_sensiveis:
        if marca in titulo and preco < 50:
            print(f"   [BLOQUEADO] {marca.upper()} a R${preco} — preço suspeito")
            return False

    # Peças de reposição (legado)
    palavras_legado = ["replacement", "reparo", "spare", "repair", "replacement part"]
    for palavra in palavras_legado:
        if palavra in titulo:
            print(f"   [BLOQUEADO] Peça de reposição: {palavra}")
            return False

    # Se passou por todos os filtros
    return True