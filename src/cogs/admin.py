import discord
import logging
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger("PontoBot.Admin")


class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.red)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()


class AdminCog(commands.Cog):
    PERIOD_TO_DAYS = {"dia": 1, "semana": 7, "mes": 30}

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.TZ = ZoneInfo("America/Sao_Paulo")

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
            # We catch specific errors from DB if possible, but generic catch is safe here for UI feedback
            logger.error(
                f"Erro ao salvar configuração para o servidor {interaction.guild_id}: {e}",
                exc_info=True,
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
            timestamp=datetime.now(self.TZ),
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
        # Confirmation Step
        view = ConfirmView()
        msg_confirm = await interaction.response.send_message(
            f"⚠️ **ATENÇÃO**: Você está prestes a limpar dados ({periodo}). Essa ação é irreversível.\nDeseja continuar?",
            view=view,
            ephemeral=True,
        )

        await view.wait()

        if view.value is None:
            await interaction.followup.send(
                "⏳ Tempo esgotado. Operação cancelada.", ephemeral=True
            )
            return
        if not view.value:
            await interaction.followup.send(
                "🛑 Operação cancelada pelo usuário.", ephemeral=True
            )
            return

        # Explicitly defer again if needed, or assume validation passed
        # Since button interaction deferred, we use followup

        data_limite = None
        if periodo != "total":
            dias = self.PERIOD_TO_DAYS.get(periodo, 0)
            data_limite = (datetime.now(self.TZ) - timedelta(days=dias)).isoformat()

        try:
            count = await self.db.clear_data(interaction.guild_id, data_limite)
        except Exception as e:
            logger.error(
                f"Erro ao limpar dados do servidor {interaction.guild_id}: {e}",
                exc_info=True,
            )
            await interaction.followup.send(
                "❌ Ocorreu um erro ao limpar os dados do banco.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="🗑️ Dados Limpos",
            description="A limpeza do banco de dados foi concluída com sucesso.",
            color=discord.Color.dark_grey(),
            timestamp=datetime.now(self.TZ),
        )
        embed.add_field(name="Registros Removidos", value=str(count), inline=True)
        periodo_label = next(
            (c.name for c in interaction.command.choices if c.value == periodo),
            periodo.capitalize(),
        )
        # Or just capitalize if not found
        embed.add_field(name="Filtro Aplicado", value=periodo.capitalize(), inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @limpar_dados.error
    @config.error
    async def admin_error_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Tratador de erros para comandos que exigem permissão de administrador."""
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Acesso Negado",
                description="Você não tem permissão para usar este comando.\nExigido: **Administrador**",
                color=discord.Color.red()
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            logger.exception(f"Erro inesperado no comando admin: {error}")
            msg = "❌ Ocorreu um erro ao processar o comando."
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
