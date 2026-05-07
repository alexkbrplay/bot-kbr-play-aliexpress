import json
import os
from datetime import datetime, timedelta
from config import MAX_POSTS_DIA_ALI

_posts_ali = 0
_data_hoje = datetime.now().date()
HISTORICO_ALI = "historico_ali.json"


def _resetar_se_novo_dia():
    global _posts_ali, _data_hoje
    hoje = datetime.now().date()
    if hoje != _data_hoje:
        _posts_ali = 0
        _data_hoje = hoje


def pode_postar_ali(ouro=False):
    _resetar_se_novo_dia()
    if ouro:
        return True
    return _posts_ali < MAX_POSTS_DIA_ALI


def registrar_post_ali():
    global _posts_ali
    _posts_ali += 1
    print(f"Posts hoje: {_posts_ali}/{MAX_POSTS_DIA_ALI}")


def pode_enviar_ali(titulo: str, ouro=False) -> bool:
    if ouro:
        return True

    titulo = titulo.lower().strip()
    dados = _carregar_historico()
    agora = datetime.now()

    for item in dados:
        if item["titulo"] == titulo:
            data_envio = datetime.fromisoformat(item["data"])
            if agora - data_envio < timedelta(days=7):
                return False
    return True


def registrar_envio_ali(titulo: str):
    titulo = titulo.lower().strip()
    dados = _carregar_historico()
    dados.append({"titulo": titulo, "data": datetime.now().isoformat()})
    _salvar_historico(dados)


def get_posts_ali():
    _resetar_se_novo_dia()
    return _posts_ali


def ultimas_ofertas():
    dados = _carregar_historico()
    return dados[-10:]


def _salvar_historico(dados):
    with open(HISTORICO_ALI, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)


def _carregar_historico():
    if not os.path.exists(HISTORICO_ALI):
        return []
    try:
        with open(HISTORICO_ALI, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []