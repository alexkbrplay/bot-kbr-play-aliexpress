import threading
import time
import asyncio
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


def dentro_do_horario():
    return HORA_INICIO <= datetime.now().hour < HORA_FIM


def tempo_restante():
    if not PROXIMA_POSTAGEM:
        return "Aguardando..."
    diff = (PROXIMA_POSTAGEM - datetime.now()).total_seconds()
    if diff <= 0:
        return "Executando..."
    return f"{int(diff//60):02d}m {int(diff%60):02d}s"


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


thread_bot = threading.Thread(target=loop_bot)
thread_bot.daemon = True
thread_bot.start()

while True:
    time.sleep(60)