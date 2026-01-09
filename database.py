import sqlite3
from datetime import datetime
import os

class Database:
    _config_cache = {}

    def __init__(self, db_path='ponto.db'):
        self.db_path = db_path
        # init_db is now called explicitly in main.py to avoid overhead on every instantiation
    
    def get_config(self, guild_id):
        """Get configuration for a guild with caching."""
        if guild_id in self._config_cache:
            return self._config_cache[guild_id]

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT guild_id, log_channel_id, mensagem_entrada, mensagem_saida, cargo_autorizado_id, timezone
            FROM config
            WHERE guild_id = ?
        ''', (guild_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            data = {
                'guild_id': row[0],
                'log_channel_id': row[1],
                'mensagem_entrada': row[2],
                'mensagem_saida': row[3],
                'cargo_autorizado_id': row[4],
                'timezone': row[5]
            }
            self._config_cache[guild_id] = data
            return data
        return None

    def set_config(self, guild_id, **kwargs):
        """Update configuration for a guild and invalidate cache."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Fetch current to merge
        cursor.execute('SELECT * FROM config WHERE guild_id = ?', (guild_id,))
        row = cursor.fetchone()

        # Defaults
        data = {
            'log_channel_id': None,
            'mensagem_entrada': None,
            'mensagem_saida': None,
            'cargo_autorizado_id': None,
            'timezone': 'America/Sao_Paulo'
        }

        if row:
            # Map based on index from SELECT * (order: guild_id, log, msg_in, msg_out, cargo, tz)
            data['log_channel_id'] = row[1]
            data['mensagem_entrada'] = row[2]
            data['mensagem_saida'] = row[3]
            data['cargo_autorizado_id'] = row[4]
            data['timezone'] = row[5]

        # Update with kwargs
        for key, value in kwargs.items():
            if key in data:
                data[key] = value

        cursor.execute('''
            INSERT OR REPLACE INTO config (guild_id, log_channel_id, mensagem_entrada, mensagem_saida, cargo_autorizado_id, timezone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (guild_id, data['log_channel_id'], data['mensagem_entrada'], data['mensagem_saida'], data['cargo_autorizado_id'], data['timezone']))

        conn.commit()
        conn.close()

        # Invalidate cache
        if guild_id in self._config_cache:
            del self._config_cache[guild_id]

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        # Enable WAL mode for better concurrency
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de configurações por servidor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                mensagem_entrada TEXT,
                mensagem_saida TEXT,
                cargo_autorizado_id INTEGER,
                timezone TEXT DEFAULT 'America/Sao_Paulo'
            )
        ''')
        
        # Check if timezone column exists (migration for existing DBs)
        try:
            cursor.execute("SELECT timezone FROM config LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE config ADD COLUMN timezone TEXT DEFAULT 'America/Sao_Paulo'")

        # Tabela de registros de ponto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                tipo TEXT NOT NULL,
                duracao_segundos INTEGER DEFAULT 0
            )
        ''')
        
        # Tabela para controle de status (ativo/pausado)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_ponto (
                user_id INTEGER,
                guild_id INTEGER,
                status TEXT DEFAULT 'inativo',
                timestamp_entrada TEXT,
                PRIMARY KEY (user_id, guild_id)
            )
        ''')

        # Índices para otimização de performance
        # Melhora performance do comando ranking (filtro por guild, tipo e data)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_registros_ranking
            ON registros (guild_id, tipo, timestamp)
        ''')

        # Melhora performance do comando relatorio (filtro por user, guild e ordenação por data)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_registros_user
            ON registros (user_id, guild_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
