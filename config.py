# ==========================================
# CONFIGURAÇÕES
# ==========================================

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# AliExpress API
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
TRACKING_ID = os.getenv("TRACKING_ID")

# Postagens
INTERVALO_SEGUNDOS = 900  # 15 minutos
MAX_POR_EXECUCAO = 1
MAX_POSTS_DIA_ALI = 100

# Regras de oferta
DESCONTO_OURO_ALI = 60
DESCONTO_MINIMO_EXIBIR = 20

# Limite de preço
PRECO_MAXIMO_RECOMENDADO = 500