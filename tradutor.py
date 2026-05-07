import re

DICIONARIO = {
    "kids smartwatch": "Smartwatch Infantil",
    "smartwatch": "Smartwatch",
    "earbuds": "Fone Bluetooth",
    "tws": "Fone Bluetooth",
    "headset": "Headset",
    "gaming headset": "Headset Gamer",
    "phone case": "Capa de Celular",
    "silicone case": "Capa de Silicone",
    "power bank": "Power Bank",
    "fast charger": "Carregador Rápido",
    "gan charger": "Carregador Rápido",
    "wireless charger": "Carregador Sem Fio",
    "mouse pad": "Mouse Pad Gamer",
    "gaming mouse": "Mouse Gamer",
    "mechanical keyboard": "Teclado Mecânico",
    "gaming keyboard": "Teclado Gamer",
    "tv box": "TV Box",
    "projector": "Projetor",
    "external ssd": "SSD Externo",
    "smart plug": "Tomada Inteligente",
    "smart bulb": "Lâmpada Inteligente",
    "action camera": "Câmera de Ação",
}

PALAVRAS_REPOSICAO = [
    "replacement", "reparo", "peça", "spare", "part",
    "battery", "cable", "adapter", "remote", "controle",
    "foam", "ear pads", "memory foam", "cushion",
    "placa", "board", "mainboard", "used",
]

def extrair_potencia(titulo: str) -> str:
    match = re.search(r'(\d+)\s*w', titulo.lower())
    return f"{match.group(1)}W" if match else ""

def extrair_comprimento(titulo: str) -> str:
    match = re.search(r'(\d+[.,]?\d*)\s*m', titulo.lower())
    return match.group(1).replace(",", ".") + "m" if match else ""

def extrair_cor(titulo: str) -> str:
    cores = {
        "black": "Preto", "white": "Branco", "red": "Vermelho",
        "blue": "Azul", "green": "Verde", "pink": "Rosa",
        "gold": "Dourado", "silver": "Prata",
    }
    for en, pt in cores.items():
        if en in titulo.lower():
            return pt
    return ""

def traduzir(titulo: str) -> str:
    titulo_lower = titulo.lower()

    for palavra in PALAVRAS_REPOSICAO:
        if palavra in titulo_lower:
            return "Peça de Reposição"

    if "hdmi" in titulo_lower:
        comprimento = extrair_comprimento(titulo)
        return f"Cabo HDMI 8K - {comprimento}" if comprimento else "Cabo HDMI 8K"

    if "smartwatch" in titulo_lower:
        if "kids" in titulo_lower:
            return "Smartwatch Infantil"
        return "Smartwatch"

    if "mouse pad" in titulo_lower:
        return "Mouse Pad Gamer"

    for en, pt in DICIONARIO.items():
        if en in titulo_lower:
            return pt

    palavras = titulo.split()[:4]
    return " ".join(palavras)