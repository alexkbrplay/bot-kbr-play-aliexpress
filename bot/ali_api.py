import random
import json
import os
from aliexpress_api import AliexpressApi
from config import APP_KEY, APP_SECRET, TRACKING_ID

ARQUIVO_INDICE = "ali_indice.json"

KEYWORDS = [
    # Áudio
    "bluetooth earbuds",
    "gaming headset",
    "smartwatch",
    "wireless earbuds",

    # Periféricos
    "gaming mouse",
    "mechanical keyboard",
    "gaming mousepad",

    # Hardware
    "nvme ssd",
    "external ssd",
    "ddr4 desktop ram",
    "ddr5 ram",
    "intel core i5",
    "intel core i7",
    "amd ryzen 5",
    "amd ryzen 7",
    "lga 1700 motherboard",
    "am4 motherboard",

    # Monitores
    "gaming monitor",
    "curved monitor",

    # Fontes
    "power supply 80 plus",
    "power supply modular",

    # TV / Stream
    "android tv box",
    "action camera",
    "smart plug",
    "smart bulb",
]

INDISPONIVEIS_BR = [
    "costume", "cosplay", "adult", "sexy", "lingerie", "car supply"
]


def _carregar_indice():
    if os.path.exists(ARQUIVO_INDICE):
        try:
            with open(ARQUIVO_INDICE, "r") as f:
                dados = json.load(f)
                return dados.get("indice", 0), dados.get("ordem", None)
        except:
            pass
    return 0, None


def _salvar_indice(indice, ordem):
    with open(ARQUIVO_INDICE, "w") as f:
        json.dump({"indice": indice, "ordem": ordem}, f)


def _proxima_keyword():
    indice, ordem = _carregar_indice()
    if not ordem or indice >= len(ordem):
        ordem = list(range(len(KEYWORDS)))
        random.shuffle(ordem)
        indice = 0
    keyword = KEYWORDS[ordem[indice]]
    _salvar_indice(indice + 1, ordem)
    return keyword


def _parse_float(valor):
    try:
        return float(str(valor).replace(",", ".").strip())
    except:
        return 0.0


def _parse_int(valor):
    try:
        return int(str(valor).replace("%", "").replace(",", "").strip())
    except:
        return 0


def buscar_produtos_ali():
    keyword = _proxima_keyword()
    print(f"[ALI] Buscando: {keyword}")

    try:
        api = AliexpressApi(APP_KEY, APP_SECRET, "EN", "BRL", TRACKING_ID)
        resposta = api.get_hotproducts(
            keywords=keyword,
            page=1,
            page_size=50,
            ship_to_country="BR"
        )

        if not resposta or not hasattr(resposta, "products"):
            print("[ALI] Sem produtos retornados")
            return []

        lista = []

        for p in resposta.products:
            try:
                if hasattr(p, "product_title_en") and p.product_title_en:
                    titulo = p.product_title_en
                elif hasattr(p, "product_title") and p.product_title:
                    titulo = p.product_title
                else:
                    titulo = ""

                titulo_lower = titulo.lower()

                bloqueado = False
                for palavra in INDISPONIVEIS_BR:
                    if palavra in titulo_lower:
                        bloqueado = True
                        break
                if bloqueado:
                    continue

                if hasattr(p, "target_sale_price") and p.target_sale_price:
                    preco_atual = _parse_float(p.target_sale_price)
                elif hasattr(p, "sale_price") and p.sale_price:
                    preco_atual = _parse_float(p.sale_price)
                else:
                    preco_atual = 0.0

                if hasattr(p, "target_original_price") and p.target_original_price:
                    preco_original = _parse_float(p.target_original_price)
                elif hasattr(p, "original_price") and p.original_price:
                    preco_original = _parse_float(p.original_price)
                else:
                    preco_original = None

                desconto = _parse_int(p.discount) if hasattr(p, "discount") and p.discount else 0
                if preco_original and preco_original > preco_atual and desconto == 0:
                    desconto = int(((preco_original - preco_atual) / preco_original) * 100)

                if preco_atual <= 0:
                    continue

                frete_gratis = False
                if hasattr(p, "free_shipping") and p.free_shipping:
                    frete_gratis = True

                ship_from = ""
                if hasattr(p, "ship_from") and p.ship_from:
                    ship_from = p.ship_from

                link = p.promotion_link if hasattr(p, "promotion_link") and p.promotion_link else p.product_detail_url

                lista.append({
                    "fonte": "ALI",
                    "title": titulo,
                    "price": round(preco_atual, 2),
                    "original_price": round(preco_original, 2) if preco_original and preco_original > preco_atual else None,
                    "discount": desconto,
                    "link": link,
                    "image": p.product_main_image_url,
                    "sold_quantity": _parse_int(p.lastest_volume) if hasattr(p, "lastest_volume") and p.lastest_volume else 0,
                    "free_shipping": frete_gratis,
                    "seller": getattr(p, "shop_name", "") or getattr(p, "store_name", "") or "",
                    "ship_from": ship_from,
                })

            except Exception as e:
                print(f"   Erro item Ali: {e}")
                continue

        print(f"[ALI] {len(lista)} produtos encontrados")
        return lista

    except Exception as e:
        print(f"[ALI] Erro na busca: {e}")
        return []