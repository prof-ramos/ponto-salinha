import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='ponto.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
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
                cargo_autorizado_id INTEGER
            )
        ''')
        
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
        
        conn.commit()
        conn.close()
