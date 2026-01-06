import aiosqlite
import os


class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "ponto.db")

    async def init_db(self):
        """Inicializa as tabelas do banco de dados se não existirem."""
        async with aiosqlite.connect(self.db_path) as db:
            # Configurações por servidor
            await db.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    guild_id INTEGER PRIMARY KEY,
                    log_channel_id INTEGER,
                    mensagem_entrada TEXT,
                    mensagem_saida TEXT,
                    cargo_autorizado_id INTEGER
                )
            """)

            # Tabela de registros
            await db.execute("""
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    guild_id INTEGER,
                    timestamp TEXT,
                    tipo TEXT,
                    duracao_segundos INTEGER
                )
            """)

            # Índices para performance
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_registros_user_guild ON registros(user_id, guild_id)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_registros_timestamp ON registros(timestamp)"
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_registros_guild_timestamp ON registros(guild_id, timestamp)"
            )

            # Controle de status
            await db.execute("""
                CREATE TABLE IF NOT EXISTS status_ponto (
                    user_id INTEGER,
                    guild_id INTEGER,
                    status TEXT DEFAULT 'inativo',
                    timestamp_entrada TEXT,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            await db.commit()

    async def get_config(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM config WHERE guild_id = ?", (guild_id,)
            ) as cursor:
                return await cursor.fetchone()

    async def set_config(
        self, guild_id: int, log_channel_id: int, cargo_autorizado_id: int = None
    ):
        """Salva ou atualiza a configuração de um servidor."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO config (guild_id, log_channel_id, cargo_autorizado_id)
                VALUES (?, ?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET
                    log_channel_id = excluded.log_channel_id,
                    cargo_autorizado_id = excluded.cargo_autorizado_id
            """,
                (guild_id, log_channel_id, cargo_autorizado_id),
            )
            await db.commit()

    async def get_user_status(self, user_id: int, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT status, timestamp_entrada FROM status_ponto
                WHERE user_id = ? AND guild_id = ?
            """,
                (user_id, guild_id),
            ) as cursor:
                return await cursor.fetchone()

    async def register_entry(self, user_id: int, guild_id: int, timestamp: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO status_ponto (user_id, guild_id, status, timestamp_entrada)
                VALUES (?, ?, 'ativo', ?)
            """,
                (user_id, guild_id, timestamp),
            )

            await db.execute(
                """
                INSERT INTO registros (user_id, guild_id, timestamp, tipo)
                VALUES (?, ?, ?, 'entrada')
            """,
                (user_id, guild_id, timestamp),
            )
            await db.commit()

    async def register_exit(
        self, user_id: int, guild_id: int, timestamp: str, duracao: int
    ):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO registros (user_id, guild_id, timestamp, tipo, duracao_segundos)
                VALUES (?, ?, ?, 'saida', ?)
            """,
                (user_id, guild_id, timestamp, duracao),
            )

            await db.execute(
                """
                UPDATE status_ponto SET status = 'inativo'
                WHERE user_id = ? AND guild_id = ?
            """,
                (user_id, guild_id),
            )
            await db.commit()

    async def get_ranking(self, guild_id: int, data_inicio: str, limit: int = 10):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT user_id, SUM(duracao_segundos) as total_segundos
                FROM registros
                WHERE guild_id = ? AND tipo = 'saida' AND timestamp >= ?
                GROUP BY user_id
                ORDER BY total_segundos DESC
                LIMIT ?
            """,
                (guild_id, data_inicio, limit),
            ) as cursor:
                return await cursor.fetchall()

    async def get_user_records(self, user_id: int, guild_id: int, limit: int = 100):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT timestamp, tipo, duracao_segundos
                FROM registros
                WHERE user_id = ? AND guild_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (user_id, guild_id, limit),
            ) as cursor:
                return await cursor.fetchall()

    async def clear_data(self, guild_id: int, data_limite: str = None):
        """Limpa registros antigos."""
        async with aiosqlite.connect(self.db_path) as db:
            if data_limite:
                await db.execute(
                    "DELETE FROM registros WHERE guild_id = ? AND timestamp < ?",
                    (guild_id, data_limite),
                )
                # Também remove status antigos para manter a integridade
                await db.execute(
                    "DELETE FROM status_ponto WHERE guild_id = ? AND timestamp_entrada < ?",
                    (guild_id, data_limite),
                )
            else:
                await db.execute(
                    "DELETE FROM registros WHERE guild_id = ?", (guild_id,)
                )
                await db.execute(
                    "DELETE FROM status_ponto WHERE guild_id = ?", (guild_id,)
                )

            await db.commit()
            return db.total_changes
