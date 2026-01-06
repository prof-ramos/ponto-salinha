import discord
import logging
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("PontoBot.Admin")


class AdminCog(commands.Cog):
    PERIOD_TO_DAYS = {"dia": 1, "semana": 7, "mes": 30}

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(
        name="config", description="Configurar canal de logs e cargo autorizado"
    )
    @app_commands.describe(
        canal_log="Canal onde os registros de ponto serão enviados",
        cargo="Cargo que terá permissão para usar o bot (opcional)",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config(
        self,
        interaction: discord.Interaction,
        canal_log: discord.TextChannel,
        cargo: discord.Role = None,
    ):
        try:
            await self.db.set_config(
                interaction.guild_id, canal_log.id, cargo.id if cargo else None
            )
        except Exception as e:
            logger.error(
                f"Erro ao salvar configuração para o servidor {interaction.guild_id}: {e}"
            )
            await interaction.response.send_message(
                "❌ Ocorreu um erro ao salvar as configurações no banco de dados.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="⚙️ Configuração Atualizada",
            description="As preferências do bot para este servidor foram salvas.",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Canal de Logs", value=canal_log.mention, inline=True)
        embed.add_field(
            name="Cargo Autorizado",
            value=cargo.mention if cargo else "Todos os membros",
            inline=True,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="limpar_dados", description="Remover registros antigos do banco de dados"
    )
    @app_commands.describe(periodo="Período de dados a serem removidos")
    @app_commands.choices(
        periodo=[
            app_commands.Choice(name="Último Dia", value="dia"),
            app_commands.Choice(name="Última Semana", value="semana"),
            app_commands.Choice(name="Último Mês", value="mes"),
            app_commands.Choice(name="Todos os Dados", value="total"),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def limpar_dados(self, interaction: discord.Interaction, periodo: str):
        await interaction.response.defer(ephemeral=True)

        data_limite = None
        if periodo != "total":
            dias = self.PERIOD_TO_DAYS.get(periodo, 0)
            data_limite = (
                datetime.now(timezone.utc) - timedelta(days=dias)
            ).isoformat()

        try:
            count = await self.db.clear_data(interaction.guild_id, data_limite)
        except Exception as e:
            logger.error(
                f"Erro ao limpar dados do servidor {interaction.guild_id}: {e}"
            )
            await interaction.followup.send(
                "❌ Ocorreu um erro ao limpar os dados do banco.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🗑️ Dados Limpos",
            description="A limpeza do banco de dados foi concluída com sucesso.",
            color=discord.Color.dark_grey(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Registros Removidos", value=str(count), inline=True)
        embed.add_field(name="Filtro Aplicado", value=periodo.capitalize(), inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
