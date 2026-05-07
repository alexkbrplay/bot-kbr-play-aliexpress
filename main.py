import threading
import time
import asyncio
import os
import sys
from datetime import datetime, timedelta

from bot import enviar_oferta
from controle import get_posts_ali, ultimas_ofertas
from config import HORA_INICIO, HORA_FIM, INTERVALO_SEGUNDOS

BOT_ATIVO = True
BUSCANDO = False
PROXIMA_POSTAGEM = None
LOGS = []


def add_log(msg):
    hora = datetime.now().strftime("%H:%M:%S")
    LOGS.append(f"[{hora}] {msg}")
    if len(LOGS) > 10:
        LOGS.pop(0)


def limpar():
    os.system("cls" if os.name == "nt" else "clear")


def dentro_do_horario():
    return HORA_INICIO <= datetime.now().hour < HORA_FIM


def tempo_restante():
    if not PROXIMA_POSTAGEM:
        return "Aguardando..."
    diff = (PROXIMA_POSTAGEM - datetime.now()).total_seconds()
    if diff <= 0:
        return "Executando..."
    return f"{int(diff//60):02d}m {int(diff%60):02d}s"


def mostrar_dashboard():
    limpar()
    print("=" * 50)
    print("      BOT KBR PLAY — ALIEXPRESS")
    print("=" * 50)

    status = "[ON]" if BOT_ATIVO else "[OFF]"
    buscando = "SIM" if BUSCANDO else "NAO"

    print(f"Status   : {status}")
    print(f"Buscando : {buscando}")
    print(f"Horario  : {datetime.now().strftime('%H:%M:%S')}")

    print("-" * 50)
    print(f"AliExpress : {get_posts_ali()} ofertas enviadas hoje")
    print("-" * 50)
    print(f"Proxima postagem: {tempo_restante()}")
    print("-" * 50)

    print("ÚLTIMAS 10 OFERTAS ENVIADAS:")
    print("-" * 50)
    ofertas = ultimas_ofertas()
    if not ofertas:
        print("  Nenhuma oferta enviada ainda")
    else:
        for item in reversed(ofertas[-10:]):
            titulo = item["titulo"]
            data = item["data"]
            hora_envio = data.split("T")[1].split(".")[0][:8]
            titulo_resumido = titulo[:35] + "..." if len(titulo) > 35 else titulo
            print(f"  {hora_envio} - {titulo_resumido}")

    print("-" * 50)
    print("ULTIMAS AÇÕES:")
    print("-" * 50)
    if not LOGS:
        print("Nenhuma ação ainda")
    else:
        for log in LOGS[-10:]:
            print(log)

    print("=" * 50)
    print("1 - Forçar busca")
    print("2 - Parar bot")
    print("3 - Sair")
    print("=" * 50)
    print("Opcao: ", end="", flush=True)


def loop_input():
    global _comando
    while True:
        try:
            opcao = sys.stdin.readline().strip()
            _comando[0] = opcao
        except:
            pass


def loop_bot():
    global BUSCANDO, PROXIMA_POSTAGEM
    while True:
        if BOT_ATIVO and dentro_do_horario():
            BUSCANDO = True
            add_log("Buscando produtos...")
            try:
                resultado = asyncio.run(enviar_oferta())
                if resultado:
                    add_log(resultado)
                else:
                    add_log("Nenhum produto enviado")
            except Exception as e:
                add_log(f"ERRO: {e}")
            BUSCANDO = False
            PROXIMA_POSTAGEM = datetime.now() + timedelta(seconds=INTERVALO_SEGUNDOS)
            time.sleep(INTERVALO_SEGUNDOS)
        else:
            BUSCANDO = False
            time.sleep(5)


_comando = [None]

thread_bot = threading.Thread(target=loop_bot)
thread_input = threading.Thread(target=loop_input)
thread_bot.daemon = True
thread_input.daemon = True
thread_bot.start()
thread_input.start()

while True:
    mostrar_dashboard()
    for _ in range(300):
        time.sleep(0.1)
        if _comando[0] is not None:
            break
    opcao = _comando[0]
    _comando[0] = None
    if opcao == "1":
        PROXIMA_POSTAGEM = datetime.now()
        add_log("Busca manual forçada")
    elif opcao == "2":
        BOT_ATIVO = False
        add_log("Bot parado")
    elif opcao == "3":
        break