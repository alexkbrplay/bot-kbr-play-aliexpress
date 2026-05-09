import os
import threading
import time
import asyncio
import sys
from datetime import datetime, timedelta

from bot import enviar_oferta
from controle import get_posts_ali, ultimas_ofertas
from config import HORA_INICIO, HORA_FIM, INTERVALO_SEGUNDOS

# ==========================================
# DETECÇÃO DE AMBIENTE
# ==========================================
BOT_MODE = os.getenv("BOT_MODE", "local")  # "local" ou "cloud"
BOT_ATIVO = True
BUSCANDO = False
PROXIMA_POSTAGEM = None
LOGS = []
_comando = [None]


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
    return f"{int(diff // 60):02d}m {int(diff % 60):02d}s"


def limpar():
    if BOT_MODE == "local":
        os.system("cls" if os.name == "nt" else "clear")


def mostrar_dashboard():
    if BOT_MODE != "local":
        return
    
    limpar()
    print("=" * 50)
    print("      BOT KBR PLAY — ALIEXPRESS")
    print("=" * 50)

    status = "[ON]" if BOT_ATIVO else "[OFF]"
    buscando = "SIM" if BUSCANDO else "NAO"

    print(f"Status   : {status}")
    print(f"Buscando : {buscando}")
    print(f"Horario  : {datetime.now().strftime('%H:%M:%S')}")
    print(f"Ambiente : {BOT_MODE.upper()}")

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
    print("1 - Iniciar/Forçar busca")
    print("2 - Parar bot")
    print("3 - Sair")
    print("=" * 50)
    print("Opcao: ", end="", flush=True)


def loop_input():
    """Apenas no modo local - aguarda comandos do usuário"""
    if BOT_MODE != "local":
        return
    
    while True:
        try:
            opcao = sys.stdin.readline().strip()
            if opcao:
                _comando[0] = opcao
        except:
            pass


def loop_bot():
    """Loop principal do bot (funciona em ambos os modos)"""
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
            time.sleep(10)


def processar_comandos():
    """Processa comandos do usuário (apenas modo local)"""
    global BOT_ATIVO, PROXIMA_POSTAGEM
    
    if BOT_MODE != "local":
        return
    
    while True:
        time.sleep(10)
        if _comando[0] is not None:
            opcao = _comando[0]
            _comando[0] = None
            
            if opcao == "1":
                if not BOT_ATIVO:
                    BOT_ATIVO = True
                    add_log("Bot iniciado")
                    print("\n✅ Bot iniciado! Pressione ENTER para continuar...")
                else:
                    PROXIMA_POSTAGEM = datetime.now()
                    add_log("Busca manual forçada")
                    print("\n🔄 Busca forçada! Pressione ENTER para continuar...")
                # Aguarda ENTER para não sobrepor o dashboard
                sys.stdin.readline()
                
            elif opcao == "2":
                BOT_ATIVO = False
                add_log("Bot parado")
                print("\n⏸️ Bot parado! Pressione ENTER para continuar...")
                sys.stdin.readline()
                
            elif opcao == "3":
                print("\n🔴 Encerrando bot...")
                sys.exit(0)


def loop_dashboard():
    """Atualiza o dashboard (apenas modo local)"""
    if BOT_MODE != "local":
        return
    
    while True:
        mostrar_dashboard()
        time.sleep(10)  # ← Atualiza a cada 10 segundos (dá tempo de digitar)


# ==========================================
# INÍCIO DO BOT
# ==========================================
if __name__ == "__main__":
    # Exibe mensagem inicial
    if BOT_MODE == "cloud":
        print("=" * 50)
        print("   BOT KBR PLAY - ALIEXPRESS")
        print("   Modo: NUVEM (automático)")
        print("=" * 50)
        print(f"Horário ativo: {HORA_INICIO}:00 às {HORA_FIM}:00")
        print(f"Intervalo: {INTERVALO_SEGUNDOS}s")
        print("=" * 50)
        print("Bot iniciado automaticamente...")
    else:
        print("=" * 50)
        print("   BOT KBR PLAY - ALIEXPRESS")
        print("   Modo: LOCAL (com dashboard)")
        print("=" * 50)
        print(f"Horário ativo: {HORA_INICIO}:00 às {HORA_FIM}:00")
        print(f"Intervalo: {INTERVALO_SEGUNDOS}s")
        print("=" * 50)
        print("Iniciando...")
    
    # Inicia o bot
    thread_bot = threading.Thread(target=loop_bot)
    thread_bot.daemon = True
    thread_bot.start()
    
    # Inicia processamento de comandos e dashboard
    if BOT_MODE == "local":
        # Thread do input
        thread_input = threading.Thread(target=loop_input)
        thread_input.daemon = True
        thread_input.start()
        
        # Thread do dashboard
        thread_dashboard = threading.Thread(target=loop_dashboard)
        thread_dashboard.daemon = True
        thread_dashboard.start()
        
        # Processa comandos (bloqueante)
        processar_comandos()
    else:
        # Modo cloud: mantém a thread principal viva
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nBot encerrado.")