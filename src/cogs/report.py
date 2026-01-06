import discord
import logging
import openpyxl
import os
import asyncio
import tempfile
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
from openpyxl.styles import Font, Alignment

logger = logging.getLogger("PontoBot.Report")


class ReportCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(
        name="relatorio", description="Gerar relatório de horas em Excel"
    )
    @app_commands.describe(
        usuario="Usuário específico para o relatório (deixe vazio para o seu)"
    )
    async def relatorio(
        self, interaction: discord.Interaction, usuario: discord.Member = None
    ):
        await interaction.response.defer(ephemeral=True)

        target = usuario or interaction.user
        guild_id = interaction.guild_id

        # Check de permissão: apenas o próprio usuário ou admin/moderador pode ver o relatório
        if target.id != interaction.user.id:
            if (
                not interaction.user.guild_permissions.administrator
                and not interaction.user.guild_permissions.manage_guild
            ):
                # Opcional: checar cargo de moderador configurado no banco aqui
                await interaction.followup.send(
                    "❌ Você não tem permissão para ver o relatório de outros usuários.",
                    ephemeral=True,
                )
                return

        try:
            registros = await self.db.get_user_records(target.id, guild_id)
        except Exception as e:
            logger.error(
                f"Erro ao buscar registros para relatório do usuário {target.id}: {e}"
            )
            await interaction.followup.send(
                "❌ Erro ao acessar o banco de dados.", ephemeral=True
            )
            return

        if not registros:
            await interaction.followup.send(
                "❌ Nenhum registro encontrado para este usuário.", ephemeral=True
            )
            return

        # Gerar Excel em uma thread separada
        loop = asyncio.get_event_loop()
        try:
            filename = await loop.run_in_executor(
                None, self._generate_excel, target, registros
            )
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo Excel para {target.id}: {e}")
            await interaction.followup.send(
                "❌ Erro ao gerar o relatório.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📊 Relatório Gerado",
            description=f"O histórico de pontos de **{target.display_name}** foi processado.",
            color=discord.Color.purple(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(
            name="Total de Registros", value=str(len(registros)), inline=True
        )

        await interaction.followup.send(
            embed=embed, file=discord.File(filename), ephemeral=True
        )

        # Limpeza
        try:
            os.remove(filename)
        except Exception as e:
            logger.error(f"Erro ao deletar arquivo temporário {filename}: {e}")

    def _generate_excel(self, target, registros):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Relatório de Ponto"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = openpyxl.styles.PatternFill(
            start_color="5865F2", end_color="5865F2", fill_type="solid"
        )
        center_align = Alignment(horizontal="center")

        # Cabeçalho
        headers = ["Data/Hora", "Tipo", "Duração"]
        for col, text in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=text)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align

        # Dados
        for idx, row in enumerate(registros, 2):
            try:
                dt = datetime.fromisoformat(row["timestamp"])
                # Garantir UTC para formatação no Excel
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                ws.cell(row=idx, column=1, value=dt.strftime("%d/%m/%Y %H:%M:%S"))
            except (ValueError, TypeError) as e:
                logger.warning(f"Timestamp inválido no registro {row.get('id')}: {e}")
                ws.cell(row=idx, column=1, value=str(row.get("timestamp", "-")))

            ws.cell(row=idx, column=2, value=row["tipo"].capitalize())

            duracao = row["duracao_segundos"]
            if row["tipo"] == "saida" and duracao:
                horas = duracao // 3600
                minutos = (duracao % 3600) // 60
                ws.cell(row=idx, column=3, value=f"{horas}h {minutos}min")
            else:
                ws.cell(row=idx, column=3, value="-")

        # Ajustar largura das colunas
        try:
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        val = str(cell.value) if cell.value is not None else ""
                        if len(val) > max_length:
                            max_length = len(val)
                    except Exception:
                        pass
                adjusted_width = max_length + 2
                ws.column_dimensions[column].width = adjusted_width
        except Exception as e:
            logger.warning(f"Erro ao ajustar larguras de coluna: {e}")

        # Gerar nome de arquivo seguro usando tempfile
        # Usamos abas para evitar problemas de path traversal com target.name
        suffix = f"_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.xlsx"
        # Criar arquivo temporário seguro
        fd, path = tempfile.mkstemp(suffix=suffix, prefix="relatorio_")
        os.close(fd)  # Fechar o file descriptor pois wb.save abrirá o arquivo

        wb.save(path)
        return path


async def setup(bot):
    await bot.add_cog(ReportCog(bot))
