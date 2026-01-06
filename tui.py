from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Label, Input, Button, TabbedContent, TabPane
from textual.containers import Container, Horizontal, Vertical
from textual.timer import Timer
from database import Database
from datetime import datetime
import pytz

# --- Tech/Future Theme CSS ---
THEME_CSS = """
Screen {
    background: #0d0221;
    color: #00ff41;
}

Header {
    dock: top;
    background: #1a0b2e;
    color: #ff00ff;
    height: 3;
    content-align: center middle;
    text-style: bold;
    border-bottom: double #00ffff;
}

Footer {
    dock: bottom;
    background: #1a0b2e;
    color: #00ffff;
    height: 1;
}

DataTable {
    background: #0d0221;
    border: heavy #ff00ff;
    color: #00ff41;
    scrollbar-color: #00ffff;
    scrollbar-background: #1a0b2e;
}

DataTable > .datatable--header {
    background: #240046;
    color: #00ffff;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: #3c096c;
    color: #ffffff;
}

.box {
    border: heavy #00ffff;
    padding: 1;
    margin: 1;
    background: #10002b;
}

Label {
    color: #ff00ff;
    text-style: bold;
}

Input {
    border: heavy #00ff41;
    background: #000000;
    color: #00ff41;
}

Button {
    background: #240046;
    color: #00ffff;
    border: heavy #ff00ff;
    text-style: bold;
}

Button:hover {
    background: #3c096c;
    color: #ffffff;
}
"""

class DBHandler:
    """Helper to interact with the database in a safe way."""
    def __init__(self):
        self.db = Database()

    def get_active_users(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, guild_id, timestamp_entrada
            FROM status_ponto
            WHERE status = 'ativo'
        ''')
        data = cursor.fetchall()
        conn.close()
        return data

    def get_recent_logs(self, limit=20):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT guild_id, user_id, tipo, timestamp, duracao_segundos
            FROM registros
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        data = cursor.fetchall()
        conn.close()
        return data

    def get_config(self, guild_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT log_channel_id, cargo_autorizado_id, timezone
            FROM config
            WHERE guild_id = ?
        ''', (guild_id,))
        data = cursor.fetchone()
        conn.close()
        return data

    def update_config(self, guild_id, log_channel_id, cargo_id, timezone):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO config (guild_id, log_channel_id, cargo_autorizado_id, timezone)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, log_channel_id, cargo_id, timezone))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

class BotDashboard(App):
    CSS = THEME_CSS
    TITLE = "CYBERPUNCH // MONITOR"
    SUB_TITLE = "Neural Link Established..."

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with TabbedContent(initial="live_ops"):
            with TabPane("LIVE OPS", id="live_ops"):
                yield Label("⚡ ACTIVE NEURAL LINKS (CLOCKED IN)")
                yield DataTable(id="active_users_table")

            with TabPane("DATA LOGS", id="data_logs"):
                yield Label("💾 SYSTEM LOGS")
                yield DataTable(id="logs_table")

            with TabPane("SYSTEM CONFIG", id="sys_config"):
                with Container(classes="box"):
                    yield Label("🔧 GUILD CONFIGURATION")
                    yield Input(placeholder="Guild ID", id="conf_guild_id", type="integer")
                    yield Button("LOAD CONFIG", id="btn_load_config", variant="primary")

                    yield Label("LOG CHANNEL ID")
                    yield Input(placeholder="Channel ID", id="conf_log_id")

                    yield Label("AUTHORIZED ROLE ID")
                    yield Input(placeholder="Role ID", id="conf_role_id")

                    yield Label("TIMEZONE")
                    yield Input(placeholder="Region/City", id="conf_timezone")

                    yield Button("UPLOAD PATCH", id="btn_save_config", variant="success")
                    yield Label("", id="config_status")

        yield Footer()

    def on_mount(self) -> None:
        self.db = DBHandler()
        self.set_interval(5, self.refresh_data)

        # Setup Tables
        table_active = self.query_one("#active_users_table", DataTable)
        table_active.add_columns("USER ID", "GUILD ID", "TIMESTAMP", "DURATION")

        table_logs = self.query_one("#logs_table", DataTable)
        table_logs.add_columns("GUILD", "USER", "TYPE", "TIMESTAMP", "DURATION")

        self.refresh_data()

    def refresh_data(self) -> None:
        # Update Active Users
        table_active = self.query_one("#active_users_table", DataTable)
        table_active.clear()

        active_users = self.db.get_active_users()
        for user_id, guild_id, ts_str in active_users:
            try:
                ts = datetime.fromisoformat(ts_str)
                # Calculate duration crudely for now (using system time as base, TUI side)
                # Ideally we should use timezone aware, but for TUI visualization, naive/local diff is okay if compatible
                # Since stored is isoformat, it might have offset.
                if ts.tzinfo:
                     now = datetime.now(ts.tzinfo)
                else:
                     now = datetime.now()

                duration = now - ts
                duration_str = str(duration).split('.')[0] # Remove microseconds
                table_active.add_row(str(user_id), str(guild_id), ts.strftime("%H:%M:%S"), duration_str)
            except Exception as e:
                table_active.add_row(str(user_id), str(guild_id), ts_str, "ERR")

        # Update Logs
        table_logs = self.query_one("#logs_table", DataTable)
        table_logs.clear()

        logs = self.db.get_recent_logs()
        for guild, user, tipo, ts_str, dur in logs:
            try:
                ts = datetime.fromisoformat(ts_str)
                ts_display = ts.strftime("%d/%m %H:%M")
            except:
                ts_display = ts_str

            dur_display = f"{dur}s" if dur else "-"

            # Styling based on type
            # We can't style individual cells easily in basic DataTable add_row without Rich Text
            # But we can use Rich Text inside.

            tipo_styled = f"[bold green]{tipo.upper()}[/]" if tipo == 'entrada' else f"[bold red]{tipo.upper()}[/]"

            table_logs.add_row(str(guild), str(user), tipo_styled, ts_display, dur_display)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_load_config":
            guild_id_input = self.query_one("#conf_guild_id", Input).value
            if not guild_id_input:
                self.query_one("#config_status").update("[red]ERR: Guild ID required[/]")
                return

            try:
                gid = int(guild_id_input)
                data = self.db.get_config(gid)
                if data:
                    self.query_one("#conf_log_id", Input).value = str(data[0]) if data[0] else ""
                    self.query_one("#conf_role_id", Input).value = str(data[1]) if data[1] else ""
                    self.query_one("#conf_timezone", Input).value = str(data[2]) if data[2] else ""
                    self.query_one("#config_status").update("[green]DATA LOADED[/]")
                else:
                     self.query_one("#config_status").update("[yellow]NO CONFIG FOUND (New?)[/]")
            except Exception as e:
                self.query_one("#config_status").update(f"[red]ERR: {e}[/]")

        elif event.button.id == "btn_save_config":
            guild_id_input = self.query_one("#conf_guild_id", Input).value
            if not guild_id_input:
                self.query_one("#config_status").update("[red]ERR: Guild ID required[/]")
                return

            try:
                gid = int(guild_id_input)
                log_id = self.query_one("#conf_log_id", Input).value
                role_id = self.query_one("#conf_role_id", Input).value
                tz = self.query_one("#conf_timezone", Input).value

                # Validation
                try:
                    pytz.timezone(tz)
                except:
                    self.query_one("#config_status").update("[red]INVALID TIMEZONE[/]")
                    return

                success = self.db.update_config(
                    gid,
                    int(log_id) if log_id else None,
                    int(role_id) if role_id else None,
                    tz
                )

                if success:
                    self.query_one("#config_status").update("[green]PATCH UPLOADED SUCCESSFULLY[/]")
                else:
                    self.query_one("#config_status").update("[red]DATABASE ERROR[/]")
            except Exception as e:
                self.query_one("#config_status").update(f"[red]ERR: {e}[/]")

if __name__ == "__main__":
    app = BotDashboard()
    app.run()
