import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='ponto.db'):
        self.db_path = db_path
        # init_db is now called explicitly in main.py to avoid overhead on every instantiation
    
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
