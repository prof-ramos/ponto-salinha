import discord
import logging
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from src.config import TIMEZONE

logger = logging.getLogger("PontoBot.Ponto")


class PontoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(
        name="ponto", description="Registrar sua entrada ou saída do trabalho"
    )
    async def ponto(self, interaction: discord.Interaction):
        # Validation: DM check
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "❌ Este comando não pode ser usado em mensagens diretas.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        guild_id = interaction.guild_id
        # Use Brazil time for consistency
        now = datetime.now(TIMEZONE)
        timestamp_atual = now.isoformat()

        try:
            status_data = await self.db.get_user_status(user_id, guild_id)
        except Exception as e:
            logger.error(f"Erro ao buscar status do usuário {user_id}: {e}")
            await interaction.followup.send(
                "❌ Erro ao acessar o banco de dados.", ephemeral=True
            )
            return

        embed = discord.Embed(timestamp=now)

        if not status_data or status_data["status"] == "inativo":
            # ENTRADA
            try:
                await self.db.register_entry(user_id, guild_id, timestamp_atual)
            except Exception as e:
                logger.error(f"Erro ao registrar entrada do usuário {user_id}: {e}")
                await interaction.followup.send(
                    "❌ Erro ao salvar registro de entrada.", ephemeral=True
                )
                return

            embed.title = "🟢 Ponto de Entrada"
            embed.description = f"Olá {interaction.user.mention}, seu ponto de entrada foi registrado com sucesso!"
            embed.color = discord.Color.green()
            embed.add_field(
                name="⏰ Horário", value=now.strftime("%H:%M:%S"), inline=True
            )
            embed.add_field(name="📅 Data", value=now.strftime("%d/%m/%Y"), inline=True)

            tipo_msg = "entrada"
            emoji = "🟢"
        else:
            # SAÍDA
            try:
                timestamp_entrada = datetime.fromisoformat(
                    status_data["timestamp_entrada"]
                )
                # Ensure incoming timestamp is aware
                if timestamp_entrada.tzinfo is None:
                    # Se não tem timezone, assumimos que foi salvo como TIMEZONE local
                    timestamp_entrada = timestamp_entrada.replace(tzinfo=TIMEZONE)
                else:
                    # Se tem timezone, convertemos para garantir consistência
                    timestamp_entrada = timestamp_entrada.astimezone(TIMEZONE)
            except (ValueError, TypeError, KeyError) as e:
                logger.error(
                    f"Erro ao processar timestamp de entrada para o usuário {user_id}: {e}"
                )
                await interaction.followup.send(
                    "❌ Erro nos dados de registro. Contate um administrador.",
                    ephemeral=True,
                )
                return

            # Clamp duration to 0 to avoid negative values
            duracao_segundos = max(0, int((now - timestamp_entrada).total_seconds()))

            try:
                await self.db.register_exit(
                    user_id, guild_id, timestamp_atual, duracao_segundos
                )
            except Exception as e:
                logger.error(f"Erro ao registrar saída do usuário {user_id}: {e}")
                await interaction.followup.send(
                    "❌ Erro ao salvar registro de saída.", ephemeral=True
                )
                return

            horas = duracao_segundos // 3600
            minutos = (duracao_segundos % 3600) // 60

            embed.title = "🔴 Ponto de Saída"
            embed.description = (
                f"Turno encerrado, {interaction.user.mention}. Bom descanso!"
            )
            embed.color = discord.Color.red()
            embed.add_field(
                name="⏰ Horário", value=now.strftime("%H:%M:%S"), inline=True
            )
            embed.add_field(
                name="⏳ Duração", value=f"{horas}h {minutos}min", inline=True
            )

            tipo_msg = "saída"
            emoji = "🔴"

        await interaction.followup.send(embed=embed)

        # Audit Log
        try:
            config = await self.db.get_config(guild_id)
            if config and config["log_channel_id"]:
                channel = interaction.guild.get_channel(config["log_channel_id"])
                # Validate channel type
                if channel and isinstance(
                    channel, (discord.TextChannel, discord.Thread)
                ):
                    log_embed = discord.Embed(
                        description=f"{emoji} {interaction.user.mention} registrou **{tipo_msg}**",
                        color=embed.color,
                        timestamp=now,
                    )
                    log_embed.set_author(
                        name=interaction.user.display_name,
                        icon_url=interaction.user.display_avatar.url
                        if interaction.user.display_avatar
                        else None,
                    )
                    if tipo_msg == "saída":
                        log_embed.add_field(
                            name="Duração", value=f"{horas}h {minutos}min"
                        )

                    await channel.send(embed=log_embed)
        except Exception as e:
            logger.warning(
                f"Erro ao enviar log de auditoria no servidor {guild_id}: {e}"
            )


async def setup(bot):
    await bot.add_cog(PontoCog(bot))
