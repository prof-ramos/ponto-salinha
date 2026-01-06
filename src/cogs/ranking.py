import discord
import logging
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("PontoBot.Ranking")


class RankingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    def _format_tempo(self, total_segundos: int) -> tuple[int, int]:
        """Converte segundos totais em horas e minutos."""
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        return horas, minutos

    @app_commands.command(
        name="ranking", description="Visualizar o ranking de horas trabalhadas"
    )
    @app_commands.describe(periodo="Período de tempo para o ranking")
    @app_commands.choices(
        periodo=[
            app_commands.Choice(name="Hoje", value="hoje"),
            app_commands.Choice(name="Esta Semana", value="semana"),
            app_commands.Choice(name="Este Mês", value="mes"),
            app_commands.Choice(name="Total", value="total"),
        ]
    )
    async def ranking(self, interaction: discord.Interaction, periodo: str = "semana"):
        await interaction.response.defer()

        now = datetime.now(timezone.utc)
        if periodo == "hoje":
            data_inicio = now.replace(
                hour=0, minute=0, second=0, microsecond=0
            ).isoformat()
        elif periodo == "semana":
            data_inicio = (now - timedelta(days=7)).isoformat()
        elif periodo == "mes":
            data_inicio = (now - timedelta(days=30)).isoformat()
        else:
            data_inicio = "2000-01-01T00:00:00Z"

        try:
            resultados = await self.db.get_ranking(interaction.guild_id, data_inicio)
        except Exception as e:
            logger.error(
                f"Erro ao buscar ranking do servidor {interaction.guild_id}: {e}"
            )
            await interaction.followup.send("❌ Erro ao processar o ranking.")
            return

        if not resultados:
            await interaction.followup.send(
                "📊 Nenhum registro encontrado para este período."
            )
            return

        embed = discord.Embed(
            title=f"🏆 Ranking de Produtividade - {periodo.capitalize()}",
            description="Os membros mais ativos do servidor.",
            color=discord.Color.gold(),
            timestamp=now,
        )

        # Discord permite no máximo 25 campos por Embed
        for idx, row in enumerate(resultados[:25], 1):
            user_id = row["user_id"]
            total_seg = row["total_segundos"] or 0

            user = interaction.guild.get_member(user_id)
            horas, minutos = self._format_tempo(total_seg)

            medalha = ["🥇", "🥈", "🥉"][idx - 1] if idx <= 3 else f"{idx}º"
            nome = user.display_name if user else f"Usuário {user_id}"

            embed.add_field(
                name=f"{medalha} {nome}",
                value=f"⏱️ **{horas}h {minutos}min**",
                inline=False,
            )

        if len(resultados) > 25:
            embed.set_footer(text=f"Mostrando top 25 de {len(resultados)} usuários.")

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(RankingCog(bot))
