import os
import logging
from typing import Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dotenv import load_dotenv

# Configuração de logging básica para este módulo, caso precise logar erros de importação
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis do arquivo .env
load_dotenv()

# Configurações Gerais
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
TIMEZONE_STR: str = os.getenv("TIMEZONE", "America/Sao_Paulo")

try:
    TIMEZONE: ZoneInfo = ZoneInfo(TIMEZONE_STR)
except ZoneInfoNotFoundError:
    logger.warning(f"Timezone inválido '{TIMEZONE_STR}', usando UTC como fallback.")
    TIMEZONE: ZoneInfo = ZoneInfo("UTC")

# Banco de Dados
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "ponto.db")

# Discord
DISCORD_TOKEN: Optional[str] = os.getenv("DISCORD_TOKEN")
