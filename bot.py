#!/usr/bin/env python3
"""
BOT PRINCIPAL - AliExpress Bot
Versão: 3.4
Data: 2026-05-09
"""

import random
import asyncio
import re
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut, RetryAfter

from ali_api import buscar_produtos_ali
from filtro import filtrar_produto
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
    DESCONTO_OURO_ALI,
    DESCONTO_MINIMO_EXIBIR
)

FRASES_URGENCIA = [
    "⏰ Últimas unidades!",
    "🔥 Vendendo rápido!",
    "⚡ Estoque limitado!",
    "💨 Corre antes que acabe!",
]

DISCLAIMER = "💡 <i>Preços podem ser ainda melhores na 1° Compra ou Promoções Relâmpago.\n\nSujeito a encargos calculados no fechamento da compra.</i>"


def formatar_preco(valor):
    return f"{valor:.2f}".replace(".", ",")


def registrar_analise(titulo, preco, desconto, motivo, aprovado):
    hora = datetime.now().strftime("%H:%M:%S")
    status = "APROVADO" if aprovado else "REPROVADO"
    with open("logs_analise.txt", "a", encoding="utf-8") as f:
        f.write(f"[{hora}] {status} | {motivo}\n")
        f.write(f"  Produto: {titulo[:80]}\n")
        f.write(f"  Preço: R${preco} | Desconto: {desconto}%\n")
        f.write("-" * 60 + "\n")


def extrair_caracteristicas(titulo: str) -> list:
    titulo_lower = titulo.lower()
    caracteristicas = []
    
    # Placas-mãe
    if "b85" in titulo_lower or "h81" in titulo_lower or "z97" in titulo_lower:
        caracteristicas.append("🖥️ Soquete LGA1150")
    if "b360" in titulo_lower or "h310" in titulo_lower or "z370" in titulo_lower:
        caracteristicas.append("🖥️ Soquete LGA1151")
    if "b450" in titulo_lower or "x570" in titulo_lower:
        caracteristicas.append("🖥️ Socket AM4")
    
    # Processadores
    if "i5" in titulo_lower or "i7" in titulo_lower:
        caracteristicas.append("⚡ Intel Core")
    if "ryzen 5" in titulo_lower or "ryzen 7" in titulo_lower:
        caracteristicas.append("⚡ AMD Ryzen")
    
    # SSDs
    if "nvme" in titulo_lower:
        caracteristicas.append("💨 NVMe PCIe")
    if "sata" in titulo_lower and "ssd" in titulo_lower:
        caracteristicas.append("💾 SATA SSD")
    
    # RAM
    if "ddr4" in titulo_lower:
        caracteristicas.append("🧠 DDR4")
    if "ddr5" in titulo_lower:
        caracteristicas.append("🧠 DDR5")
    if "16gb" in titulo_lower:
        caracteristicas.append("📊 16GB")
    if "32gb" in titulo_lower:
        caracteristicas.append("📊 32GB")
    
    # Fones
    if "anc" in titulo_lower:
        caracteristicas.append("🔇 Cancelamento de Ruído")
    if "bluetooth" in titulo_lower and "ear" in titulo_lower:
        caracteristicas.append("📡 Bluetooth")
    
    # Mouse pads
    if "rgb" in titulo_lower and ("mouse" in titulo_lower or "pad" in titulo_lower):
        caracteristicas.append("🌈 Iluminação RGB")
    if "xxl" in titulo_lower or "900x400" in titulo_lower:
        caracteristicas.append("📏 Tamanho XXL")
    
    return caracteristicas[:4]


def gerar_titulo_anuncio(titulo_traduzido: str, ouro: bool) -> str:
    """Gera título chamativo baseado no produto"""
    titulo_curto = titulo_traduzido[:45]
    
    if ouro:
        return f"🏆 {titulo_curto}"
    else:
        emojis = ["🔥", "⚡", "🎯", "💥", "🚀", "💎"]
        return f"{random.choice(emojis)} {titulo_curto}"


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

    enviados = 0
    analisados = 0

    for p in produtos:
        analisados += 1
        if enviados >= MAX_POR_EXECUCAO:
            break

        try:
            desconto = p.get("discount", 0)
            ouro = desconto >= DESCONTO_OURO_ALI
            preco = p.get("price", 0)
            titulo_produto = p.get("title", "")
            ship_from = p.get("ship_from", "")
            frete_gratis = p.get("free_shipping", False)

            # Aplica o filtro
            if not filtrar_produto(p):
                registrar_analise(titulo_produto, preco, desconto, "Filtro bloqueou", False)
                continue

            if not pode_postar_ali(ouro=ouro):
                registrar_analise(titulo_produto, preco, desconto, "Limite diário", False)
                return "Limite diário atingido"

            if not pode_enviar_ali(titulo_produto, ouro=ouro):
                registrar_analise(titulo_produto, preco, desconto, "Já enviado antes", False)
                continue

            registrar_analise(titulo_produto, preco, desconto, "Aprovado - enviando", True)

            # Traduz título
            titulo_traduzido = traduzir(titulo_produto)
            
            # Resumo do título (primeiros 55 caracteres)
            titulo_resumido = titulo_traduzido[:55] + ("..." if len(titulo_traduzido) > 55 else "")
            
            # Características específicas
            caracteristicas = extrair_caracteristicas(titulo_produto)

            # Monta linha de preço
            preco_original = p.get("original_price")
            if preco_original and desconto >= DESCONTO_MINIMO_EXIBIR:
                linha_preco = f"💰 <b>R$ {formatar_preco(preco)}</b>  (De R$ {formatar_preco(preco_original)})"
            else:
                linha_preco = f"💰 <b>R$ {formatar_preco(preco)}</b>"

            # Monta linha de frete
            linha_frete = "🚚 <b>Frete grátis</b>" if frete_gratis else ""
            
            # Monta linha de origem
            linha_br = "🇧🇷 <b>Envio do Brasil</b>" if "BR" in ship_from.upper() else ""

            # Título do anúncio
            titulo_anuncio = gerar_titulo_anuncio(titulo_resumido, ouro)

            # Monta mensagem
            mensagem = f"<b>{titulo_anuncio}</b>\n\n"
            
            if caracteristicas:
                for carac in caracteristicas:
                    mensagem += f"{carac}\n"
                mensagem += "\n"
            
            mensagem += f"{linha_preco}\n"
            
            if linha_frete:
                mensagem += f"{linha_frete}\n"
            if linha_br:
                mensagem += f"{linha_br}\n"
            
            mensagem += f"\n{random.choice(FRASES_URGENCIA)}\n\n"
            mensagem += DISCLAIMER

            teclado = [[InlineKeyboardButton("👉 COMPRAR AGORA", url=p["link"])]]

            sucesso, erro = await enviar_mensagem(CHAT_ID, p["image"], mensagem, InlineKeyboardMarkup(teclado))

            if sucesso:
                print(f"  [ENVIADO] {titulo_resumido}")
                registrar_post_ali()
                registrar_envio_ali(titulo_produto)
                enviados += 1
                await asyncio.sleep(10)
            else:
                print(f"  [ERRO] Falha ao enviar: {erro}")
                await asyncio.sleep(5)

        except Exception as e:
            print(f"  [ERRO] {e}")
            await asyncio.sleep(3)

    if enviados > 0:
        return f"{analisados} analisados | {enviados} enviado"
    else:
        return f"{analisados} analisados | nenhum enviado"