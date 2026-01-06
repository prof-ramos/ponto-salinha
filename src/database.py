import aiosqlite
import os
import logging
from typing import Optional, Any
from aiosqlite import Error as SQLiteError

logger = logging.getLogger(__name__)

MAX_LIMIT = 1000


class DatabaseError(Exception):
    """Custom exception for database errors."""

    pass


class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "ponto.db")
        self._validate_db_path()

    def _validate_db_path(self):
        """Validates that the database path is writable."""
        if self.db_path == ":memory:":
            return

        directory = os.path.dirname(self.db_path)
        if not directory:
            directory = "."

        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                raise DatabaseError(
                    f"Could not create database directory: {directory}"
                ) from e

        if not os.access(directory, os.W_OK):
            raise DatabaseError(f"Database directory is not writable: {directory}")

    async def init_db(self):
        """Inicializa as tabelas do banco de dados se não existirem."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable WAL mode for better concurrency
                await db.execute('PRAGMA journal_mode=WAL;')

                # Configurações por servidor
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS config (
                        guild_id INTEGER PRIMARY KEY,
                        log_channel_id INTEGER,
                        mensagem_entrada TEXT,
                        mensagem_saida TEXT,
                        cargo_autorizado_id INTEGER,
                        timezone TEXT DEFAULT 'America/Sao_Paulo'
                    )
                """)

                # Migration: add timezone column if it doesn't exist
                try:
                    await db.execute("SELECT timezone FROM config LIMIT 1")
                except Exception:
                    await db.execute("ALTER TABLE config ADD COLUMN timezone TEXT DEFAULT 'America/Sao_Paulo'")

                # Tabela de registros
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS registros (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        guild_id INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        tipo TEXT NOT NULL,
                        duracao_segundos INTEGER,
                        FOREIGN KEY (guild_id) REFERENCES config (guild_id)
                    )
                """)

                # Índices otimizados para performance
                # Melhora performance do comando ranking (filtro por guild, tipo e data)
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_registros_ranking
                    ON registros (guild_id, tipo, timestamp)
                """)

                # Melhora performance do comando relatorio (filtro por user, guild e ordenação por data)
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_registros_user
                    ON registros (user_id, guild_id, timestamp)
                """)

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
                logger.info("Database initialized successfully.")
        except SQLiteError as e:
            logger.exception("Error initializing database")
            raise DatabaseError("Failed to initialize database") from e

    async def get_config(self, guild_id: int):
        if not isinstance(guild_id, int):
            raise ValueError("guild_id must be an integer")

        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM config WHERE guild_id = ?", (guild_id,)
                ) as cursor:
                    return await cursor.fetchone()
        except SQLiteError as e:
            logger.error(f"Error fetching config for guild {guild_id}", exc_info=True)
            raise DatabaseError(f"Failed to get config for guild {guild_id}") from e

    async def set_config(
        self, guild_id: int, log_channel_id: int, cargo_autorizado_id: int = None
    ):
        """Salva ou atualiza a configuração de um servidor."""
        if not isinstance(guild_id, int) or guild_id <= 0:
            raise ValueError("Invalid guild_id")
        if not isinstance(log_channel_id, int) or log_channel_id <= 0:
            raise ValueError("Invalid log_channel_id")
        if cargo_autorizado_id is not None and (
            not isinstance(cargo_autorizado_id, int) or cargo_autorizado_id <= 0
        ):
            raise ValueError("Invalid cargo_autorizado_id")

        try:
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
        except SQLiteError as e:
            logger.error(f"Error setting config for guild {guild_id}", exc_info=True)
            raise DatabaseError(f"Failed to set config for guild {guild_id}") from e

    async def get_user_status(self, user_id: int, guild_id: int) -> Optional[Any]:
        """
        Retrieves the current status of a user in a guild.

        Returns:
            aiosqlite.Row or None: Row with 'status' and 'timestamp_entrada' if found, else None.
        """
        try:
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
        except SQLiteError as e:
            logger.error(
                f"Error getting status for user {user_id} in guild {guild_id}",
                exc_info=True,
            )
            raise DatabaseError("Failed to get user status") from e

    async def register_entry(self, user_id: int, guild_id: int, timestamp: str):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Use UPESRT with logic to preserve timestamp if already active
                await db.execute(
                    """
                    INSERT INTO status_ponto (user_id, guild_id, status, timestamp_entrada)
                    VALUES (?, ?, 'ativo', ?)
                    ON CONFLICT(user_id, guild_id) DO UPDATE SET
                        status = 'ativo',
                        timestamp_entrada = CASE WHEN status != 'ativo' THEN excluded.timestamp_entrada ELSE status_ponto.timestamp_entrada END
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
        except SQLiteError as e:
            logger.error(f"Error registering entry for user {user_id}", exc_info=True)
            raise DatabaseError("Failed to register entry") from e

    async def register_exit(
        self, user_id: int, guild_id: int, timestamp: str, duracao: int
    ):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if user was actually active
                async with db.execute(
                    "SELECT status FROM status_ponto WHERE user_id = ? AND guild_id = ?",
                    (user_id, guild_id),
                ) as cursor:
                    row = await cursor.fetchone()
                    if not row or row[0] != "ativo":
                        logger.warning(
                            f"Registering exit for user {user_id} who is not marked as active."
                        )

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
        except SQLiteError as e:
            logger.error(f"Error registering exit for user {user_id}", exc_info=True)
            raise DatabaseError("Failed to register exit") from e

    async def get_ranking(self, guild_id: int, data_inicio: str, limit: int = 10):
        if limit < 1:
            limit = 10
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        try:
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
        except SQLiteError as e:
            logger.error(f"Error fetching ranking for guild {guild_id}", exc_info=True)
            raise DatabaseError("Failed to get ranking") from e

    async def get_user_records(self, user_id: int, guild_id: int, limit: int = 100):
        if limit < 1:
            limit = 100
        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        try:
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
        except SQLiteError as e:
            logger.error(f"Error fetching records for user {user_id}", exc_info=True)
            raise DatabaseError("Failed to get user records") from e

    async def clear_data(self, guild_id: int, data_limite: str = None):
        """Limpa registros antigos."""
        try:
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
        except SQLiteError as e:
            logger.error(f"Error clearing data for guild {guild_id}", exc_info=True)
            raise DatabaseError("Failed to clear data") from e
