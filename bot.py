import random
import asyncio
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut, RetryAfter

from ali_api import buscar_produtos_ali
from filtro import filtrar_produto
from avaliador import produto_aprovado, calcular_score
from tradutor import traduzir
from controle import (
    pode_postar_ali,
    registrar_post_ali,
    pode_enviar_ali,
    registrar_envio_ali
)
from config import (
    TELEGRAM_TOKEN,
    CHAT_ID,
    MAX_POR_EXECUCAO,
    DESCONTO_OURO_ALI
)

FRASES_URGENCIA = [
    "⏰ Últimas unidades!",
    "🔥 Vendendo rápido!",
    "⚡ Estoque limitado!",
    "💨 Corre antes que acabe!",
]

FRASES_ECONOMIA = [
    "💰 Economia gigante!",
    "🎁 Imperdível!",
    "⭐ Melhor preço!",
    "🚀 Oferta relâmpago!",
]

DISCLAIMER = "💡 <i>Preços podem ser ainda melhores na 1° Compra ou Promoções Relâmpago.\n\nSujeito a encargos calculados no fechamento da compra.</i>"


def formatar_preco(valor):
    return f"{valor:.2f}".replace(".", ",")


def registrar_analise(titulo, preco, desconto, score, motivo, aprovado):
    hora = datetime.now().strftime("%H:%M:%S")
    status = "APROVADO" if aprovado else "REPROVADO"
    with open("logs_analise.txt", "a", encoding="utf-8") as f:
        f.write(f"[{hora}] {status} | {motivo}\n")
        f.write(f"  Produto: {titulo[:80]}\n")
        f.write(f"  Preço: R${preco} | Desconto: {desconto}% | Score: {score}\n")
        f.write("-" * 60 + "\n")


def extrair_caracteristicas(titulo: str) -> list:
    titulo_lower = titulo.lower()
    caracteristicas = []
    if "heart rate" in titulo_lower:
        caracteristicas.append("❤️ Mede batimentos cardíacos")
    if "blood pressure" in titulo_lower:
        caracteristicas.append("🩸 Mede pressão arterial")
    if "bluetooth call" in titulo_lower:
        caracteristicas.append("📞 Chamada Bluetooth")
    if "amoled" in titulo_lower:
        caracteristicas.append("🌈 Tela AMOLED")
    if "gps" in titulo_lower:
        caracteristicas.append("📍 GPS integrado")
    if "waterproof" in titulo_lower:
        caracteristicas.append("💧 À prova d'água")
    if "anc" in titulo_lower:
        caracteristicas.append("🔇 Cancela ruído")
    if "gaming" in titulo_lower:
        caracteristicas.append("🎮 Modo gamer")
    return caracteristicas[:3]


async def enviar_mensagem(chat_id, photo, caption, reply_markup):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return True, None
    except TimedOut as e:
        return False, f"Timeout: {e}"
    except RetryAfter as e:
        return False, f"Rate limit: aguardar {e.retry_after}s"
    except Exception as e:
        return False, str(e)


async def enviar_oferta():
    print("\n--- Buscando no AliExpress ---")

    try:
        produtos = buscar_produtos_ali()
    except Exception as e:
        print(f"[ERRO BUSCA] {e}")
        return f"ERRO BUSCA: {e}"

    if not produtos:
        return "Nenhum produto encontrado"

    for p in produtos:
        try:
            p["_score"] = calcular_score(p)
        except:
            p["_score"] = 0

    produtos = sorted(produtos, key=lambda x: x["_score"], reverse=True)

    enviados = 0
    analisados = 0

    for p in produtos:
        analisados += 1
        if enviados >= MAX_POR_EXECUCAO:
            break

        try:
            desconto = p.get("discount", 0)
            ouro = desconto >= DESCONTO_OURO_ALI
            score = p.get("_score", 0)
            preco = p.get("price", 0)
            titulo_produto = p.get("title", "")
            ship_from = p.get("ship_from", "")

            if preco <= 0:
                registrar_analise(titulo_produto, preco, desconto, score, "Preço inválido", False)
                continue

            if preco < 15 and desconto > 50:
                registrar_analise(titulo_produto, preco, desconto, score, "Preço suspeito", False)
                continue

            if not filtrar_produto(p):
                registrar_analise(titulo_produto, preco, desconto, score, "Filtro bloqueou", False)
                continue

            if not produto_aprovado(p) and not ouro:
                registrar_analise(titulo_produto, preco, desconto, score, f"Score {score} abaixo do mínimo", False)
                continue

            if not pode_postar_ali(ouro=ouro):
                registrar_analise(titulo_produto, preco, desconto, score, "Limite diário", False)
                return "Limite diário atingido"

            if not pode_enviar_ali(titulo_produto, ouro=ouro):
                registrar_analise(titulo_produto, preco, desconto, score, "Já enviado antes", False)
                continue

            registrar_analise(titulo_produto, preco, desconto, score, "Preparando envio", True)

            nome_original = traduzir(titulo_produto)
            caracteristicas = extrair_caracteristicas(titulo_produto)

            palavras_nome = nome_original.split()[:5]
            nome_resumido = " ".join(palavras_nome)

            titulo_oferta = "🏆 SUPER OFERTA DE OURO" if ouro else random.choice(["🔥 OFERTA IMPERDÍVEL", "⚡ OFERTA RELÂMPAGO", "🎯 MELHOR PREÇO"])

            mensagem = f"<b>{titulo_oferta}</b>\n\n"
            mensagem += f"📦 <b>{nome_resumido}</b>\n\n"
            mensagem += f"💰 <b>R$ {formatar_preco(preco)}</b>\n\n"

            if caracteristicas:
                for carac in caracteristicas:
                    mensagem += f"{carac}\n"
                mensagem += "\n"

            if p.get("free_shipping", False):
                mensagem += f"🚚 <b>Frete grátis</b>\n"

            if ship_from == "BR":
                mensagem += f"🇧🇷 <b>Envio do Brasil</b>\n"

            mensagem += f"\n{random.choice(FRASES_URGENCIA)}\n"
            mensagem += f"{random.choice(FRASES_ECONOMIA)}\n\n"
            mensagem += DISCLAIMER

            teclado = [[InlineKeyboardButton("👉 COMPRAR AGORA", url=p["link"])]]

            sucesso, erro = await enviar_mensagem(CHAT_ID, p["image"], mensagem, InlineKeyboardMarkup(teclado))

            if sucesso:
                print(f"  [ENVIADO] {nome_resumido}")
                registrar_analise(titulo_produto, preco, desconto, score, "Enviado com sucesso", True)
                registrar_post_ali()
                registrar_envio_ali(titulo_produto)
                enviados += 1
                await asyncio.sleep(10)
            else:
                print(f"  [ERRO] Falha ao enviar: {erro}")
                registrar_analise(titulo_produto, preco, desconto, score, f"Erro envio: {erro}", False)
                await asyncio.sleep(5)

        except Exception as e:
            print(f"  [ERRO] {e}")
            await asyncio.sleep(3)

    if enviados > 0:
        return f"{analisados} analisados | {enviados} enviado"
    else:
        return f"{analisados} analisados | nenhum enviado"