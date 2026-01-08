import discord
from discord.ext import commands
import os
import asyncio
import sys
from dotenv import load_dotenv
import logging
from database import Database
from config import DISCORD_TOKEN

# Configuração de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PontoBot")

# Carregar variáveis de ambiente
load_dotenv()


class PontoBot(commands.Bot):
    def __init__(self, db: Database) -> None:
        intents = discord.Intents.default()
        intents.members = True
        # Setting command_prefix to empty list as we primarily use Slash Commands
        super().__init__(command_prefix=[], intents=intents)
        self.db = db

    async def setup_hook(self):
        """Inicializa o banco de dados e carrega os Cogs."""
        try:
            await self.db.init_db()
        except Exception as e:
            logger.error(f"Erro ao inicializar o banco de dados: {e}")
            raise e

        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        if not os.path.isdir(cogs_dir):
            logger.warning(f"Diretório de Cogs não encontrado: {cogs_dir}")
            return

        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"Cog carregado: {filename}")
                except Exception as e:
                    logger.error(f"Erro ao carregar cog {filename}: {e}")

        # Sincronizar comandos slash
        try:
            synced = await self.tree.sync()
            logger.info(f"{len(synced)} comandos slash sincronizados.")
        except Exception as e:
            logger.error(f"Erro ao sincronizar comandos: {e}")

    async def on_ready(self):
        logger.info(f"Bot online como {self.user}")
        await self.change_presence(activity=discord.Game(name="/ponto"))


async def main():
    try:
        db = Database()
    except Exception as e:
        logger.critical(f"Erro fatal ao criar conexão com banco: {e}")
        return

    bot = PontoBot(db)
    async with bot:
        if not DISCORD_TOKEN:
            logger.critical("DISCORD_TOKEN não encontrado nas configurações ou arquivo .env")
            return

        try:
            await bot.start(DISCORD_TOKEN)
        except Exception as e:
            logger.critical(f"Falha ao iniciar conexão com Discord: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot desligado manualmente (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Erro não tratado na execução principal: {e}", exc_info=True)
        sys.exit(1)
