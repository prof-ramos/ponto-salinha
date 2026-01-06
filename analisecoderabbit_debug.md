Starting CodeRabbit review in plain text mode...

Connecting to review service
Setting up
Analyzing
Reviewing

============================================================================
File: requirements.txt
Line: 3 to 10
Type: potential_issue

Prompt for AI Agent:
In @requirements.txt around lines 3 - 10, O arquivo requirements.txt contém marcadores de conflito Git ('>>>>>>') entre dois blocos (HEAD com "aiosqlite>=0.19.0" e "python-dotenv>=1.0.0" e origin/main com "pytz==2025.2" e "textual==7.0.0"); remova todos os marcadores de conflito e resolva o conflito decidindo se mantém apenas um dos lados ou combina ambos — por exemplo, juntar as quatro dependências em linhas separadas sem marcadores se todas forem necessárias — garantindo que o arquivo final contenha apenas pacotes válidos (aiosqlite, python-dotenv, pytz, textual) cada um em sua própria linha e sem quaisquer tokens de conflito.



============================================================================
File: .claude/settings.local.json
Line: 7 to 8
Type: nitpick

Prompt for AI Agent:
In @.claude/settings.local.json around lines 7 - 8, Você adicionou o padrão permissivo "Bash(git merge:)" que permite merges com qualquer argumento; remova ou restrinja esse wildcard — por exemplo substituir "Bash(git merge:)" por padrões específicos de comando (como "Bash(git merge --no-ff:)" ou comandos aprovados sem wildcard) ou eliminar totalmente a permissão de merge e documentar/alternar para uma política que exija revisões/branches protegidas; ajuste a entrada que contém "Bash(git commit:)" e "Bash(git merge:*)" para refletir permissões mínimas e adicione notas sobre exigência de proteções de branch e revisões conforme a política do projeto.



============================================================================
File: coderabbit.yaml
Line: 1 to 6
Type: potential_issue

Prompt for AI Agent:
In @coderabbit.yaml around lines 1 - 6, O arquivo de configuração foi criado sem o ponto inicial no nome; renomeie o arquivo de coderabbit.yaml para .coderabbit.yaml (adicione o ponto no início) para que o CodeRabbit reconheça a configuração, e atualize quaisquer referências ao nome antigo em scripts/CI/docs (por exemplo, verificações que apontem para "coderabbit.yaml") para usar ".coderabbit.yaml".



============================================================================
File: coderabbit.yaml
Line: 14
Type: potential_issue

Prompt for AI Agent:
In @coderabbit.yaml at line 14, O campo auto_title_instructions em coderabbit.yaml está configurado com "humor extremamente pesado", que pode criar títulos ofensivos; atualize esse valor para uma opção mais moderada (por exemplo "humor leve" ou "criativo") e, se houver validação/configuração adicional, ajuste/adicione uma regra que restrinja termos potencialmente ofensivos para evitar que configurações futuras usem linguagem inadequada.



============================================================================
File: coderabbit.yaml
Line: 81 to 87
Type: nitpick

Prompt for AI Agent:
In @coderabbit.yaml around lines 81 - 87, The configuration currently enables ruff, pylint and flake8 simultaneously which causes duplicate linting; disable flake8 by setting its enabled flag to false (leave ruff.enabled true and keep pylint.enabled only if you require specific pylint rules), and remove any redundant flake8 configuration entries so only ruff (or ruff + pylint) runs.



============================================================================
File: main.py
Line: 217 to 244
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 217 - 244, The DB connection opened via Database().get_connection() and cursor is closed only at the end, so any exception between line 218 and 244 will leak the connection; wrap the connection and cursor usage in a try/finally (or use a context manager) around the block that computes data_inicio, executes cursor.execute(...) and fetches resultados, ensuring conn.close() (and cursor.close() if applicable) always runs in the finally; reference Database, get_connection, cursor.execute, resultados and conn.close when locating the code to modify.



============================================================================
File: main.py
Line: 1 to 10
Type: nitpick

Prompt for AI Agent:
In @main.py around lines 1 - 10, O arquivo abre conexões ao banco sem garantia de fechamento; implemente um context manager na classe Database (ex.: Database.get_cursor or Database.__enter__/__exit__) que obtém a conexão via Database.get_connection, yields um cursor, faz commit no sucesso e fecha a conexão no finally, e então refatore os callsites no main.py para usar "with db.get_cursor() as cursor:" em vez de abrir/fechar manualmente; alternativa aceitável é criar um decorator reutilizável que garanta commit/close em qualquer função que use a conexão.



============================================================================
File: main.py
Line: 134 to 193
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 134 - 193, Connection is opened with Database().get_connection() and closed at the end but not protected by try/finally, risking leaked connections on exceptions; wrap the DB usage (conn = db.get_connection(), cursor = conn.cursor(), all execute/commit/queries) in a try/finally so conn.close() always runs, and perform conn.commit() only on success (commit in the try before leaving or after successful operations) and conn.rollback() in except if desired; keep the existing timezone handling around datetime.fromisoformat(result[1]) / get_guild_timezone(interaction.guild_id) unchanged and ensure any early returns or exceptions still go through the finally block to close the connection.



============================================================================
File: main.py
Line: 366 to 390
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 366 - 390, O problema é que em periodo == "total" você executa dois DELETEs (as chamadas cursor.execute dentro do bloco periodo == "total") mas usa cursor.rowcount uma única vez (variável linhas) após o último DELETE, então o total exibido está errado; corrija somando os rowcount de cada operação ou, preferencialmente, calcule o total antes do DELETE com SELECT COUNT(*) WHERE guild_id = ? e use esse valor como linhas, então execute os DELETEs normalmente; atualize a variável linhas com a soma/valor correto antes de conn.commit() e antes de chamar interaction.response.send_message para exibir o número correto.



============================================================================
File: main.py
Line: 67 to 77
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 67 - 77, The Database().init_db() call in on_ready lacks error handling so a DB init failure leaves the bot running; wrap the init in a try/except inside on_ready (around Database().init_db()) and on error log the exception (include error details) and stop the bot cleanly (e.g., await bot.close() or call sys.exit(1)) so the process does not continue without a working DB; ensure you catch both synchronous and potential coroutine errors if init_db can be async.



============================================================================
File: main.py
Line: 333 to 345
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 333 - 345, The temp file created as filename after wb.save may not be removed if interaction.followup.send raises an exception; wrap the send (and any follow-up await) in a try/finally where filename is deleted in the finally block (use os.remove(filename) inside finally with a safe except to log errors), keeping wb.save(filename) before the try and referencing the filename variable, interaction.followup.send call, and the os.remove call to locate and update the code.



============================================================================
File: main.py
Line: 94 to 120
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 94 - 120, The DB connection can leak if an exception occurs between creating conn = db.get_connection() and conn.close(); wrap the DB operations in a try/finally (or use the connection context manager) so that conn.close() always runs and the cursor is closed; specifically, modify the block around Database(), db.get_connection(), cursor = conn.cursor(), the timezone validation, the INSERT/REPLACE, conn.commit() and conn.close() so that cursor and conn are closed in finally (or use "with db.get_connection() as conn" and a "with conn.cursor() as cursor" pattern) to guarantee cleanup on error.



============================================================================
File: main.py
Line: 36 to 64
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 36 - 64, The function check_authorized_role can leak the DB connection if an exception occurs between db.get_connection() and conn.close(); fix by using a context manager or try/finally to ensure both cursor and connection are always closed (e.g., acquire conn = db.get_connection(), create cursor, run query inside a with or try block and close cursor/conn in finally or use connection.cursor() as cursor if supported), handle exceptions from cursor.execute()/fetchone() to still send the ephemeral error response, and ensure the function signature includes the explicit return type hint "-> bool" (reference symbols: check_authorized_role, Database, get_connection, cursor, cursor.execute, conn.close).



============================================================================
File: tui.py
Line: 83 to 290
Type: nitpick

Prompt for AI Agent:
In @tui.py around lines 83 - 290, DBHandler opens and closes a new DB connection on every call and lacks error logging/validation; refactor DBHandler to reuse a single connection or implement a simple pool (e.g., keep self.conn and reuse in get_active_users, get_recent_logs, get_config, update_config with proper thread-safety/connection-liveness checks), add structured logging via Python's logging module in those methods to record query errors and durations, make refresh_data timestamp parsing more robust in refresh_data by validating/handling timezone-aware ISO strings and increment a parse-error metric when parsing fails, and tighten input validation in on_button_pressed before int conversions (validate guild_id/log_id/role_id formats and handle empty/invalid values gracefully) while ensuring update_config returns detailed errors via logs rather than silent False.



============================================================================
File: tui.py
Line: 83 to 86
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 83 - 86, Add explicit type hints to the DBHandler class and its initializer: annotate the class attribute self.db as Database (or Database | None if it can be unset), add the __init__ signature def __init__(self) -> None, and import any required types (e.g., from typing or the Database class) so static type checkers can validate usage of DBHandler and its db attribute; update references to DBHandler.db elsewhere if you change it to Optional/None to satisfy the new annotation.



============================================================================
File: main.py
Line: 18 to 28
Type: potential_issue

Prompt for AI Agent:
In @main.py around lines 18 - 28, The function get_guild_timezone is missing type hints, lacks exception handling and may leak DB connections or raise on invalid timezone strings; add proper type annotations (e.g., def get_guild_timezone(guild_id: int) -> pytz.tzinfo.BaseTzInfo), use a try/finally or context-manager around Database().get_connection() and cursor usage to ensure conn.close() always runs, validate res before calling pytz.timezone (catch pytz.UnknownTimeZoneError and ValueError), and on any DB or timezone error return the fallback pytz.timezone('America/Sao_Paulo') while logging the error for diagnostics; reference get_guild_timezone, Database.get_connection, cursor.execute and pytz.timezone when making the changes.



============================================================================
File: tui.py
Line: 100 to 111
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 100 - 111, The get_recent_logs method leaks DB connections and lacks type hints; update get_recent_logs(self, limit: int = 20) -> List[Tuple[Any, ...]] (or a more specific tuple type) to acquire the connection via a context manager or ensure conn is closed in a try/finally around cursor.execute/fetchall, e.g., use self.db.get_connection() in a with-statement if supported or explicitly close conn in finally, and keep returning the fetched data; reference get_recent_logs, self.db.get_connection, cursor.execute and conn.close when applying the fix.



============================================================================
File: tui.py
Line: 1 to 7
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 1 - 7, The file is missing typing imports and therefore has no type hints; add a typing import (e.g., add "from typing import Any, Optional, List, Dict, Tuple, Callable, Iterable" and/or "from typing import TYPE_CHECKING") or "from __future__ import annotations" at the top, then annotate all functions and methods in this module (including any App subclass methods like on_mount, compose/compose_result/compose, event handlers, and public helpers) with appropriate return types and parameter types (e.g., -> None, -> ComposeResult, -> Timer, param: Optional[str], etc.); ensure you import any concrete types you use from typing and annotate class attributes and variables used by the Textual widgets (Header, Footer, DataTable, Static, Label, Input, Button, TabbedContent, TabPane) where applicable.



============================================================================
File: tui.py
Line: 88 to 98
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 88 - 98, get_active_users leaks DB connections and lacks return type hints; fix by using a context manager or try/finally around self.db.get_connection() and the cursor to ensure conn.close() always runs (e.g., use "with self.db.get_connection() as conn:" or contextlib.closing(self.db.get_connection()) and "with conn.cursor() as cursor:"), add an explicit return type annotation (e.g., -> list[tuple] or a more specific type) on get_active_users, and ensure any exceptions still close the connection/cursor so resources are always released.



============================================================================
File: database.py
Line: 40 to 73
Type: potential_issue




============================================================================
File: implementation_plan.md
Line: 11 to 26
Type: potential_issue

Prompt for AI Agent:
In @implementation_plan.md around lines 11 - 26, The implementation currently uses synchronous sqlite3 and blocking methods while the plan and review require aiosqlite async methods; refactor src/database.py by converting the Database class to async usage: make __init__ store db_path and add async get_connection (or make __aenter__/__aexit__), convert init_db, register_entry, register_exit, clear_data, get_user_records and set_config into async def that use await with aiosqlite.connect and async context managers, catch aiosqlite.Error and re-raise a custom DatabaseError, and then implement the planned logic fixes (replace INSERT OR REPLACE in register_entry with SELECT->INSERT/UPDATE, validate user state in register_exit, safe total_changes in clear_data, validate limit/MAX_LIMIT in get_user_records, and validate positive integers in set_config); update any callers to await these new async methods.



============================================================================
File: tui.py
Line: 125 to 138
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 125 - 138, No método update_config adicione anotações de tipo para os parâmetros e retorno (por exemplo: guild_id: int, log_channel_id: Optional[int], cargo_id: Optional[int], timezone: str) e valide os parâmetros opcionais antes de executar a query (tratar None ou lançar/retornar False com mensagem clara); capture e registre a exceção em vez de silenciá‑la (usar o logger disponível ou reabrir a exceção com logging dentro do bloco except) e mantenha o fechamento da conexão em finally; referencie update_config, self.db.get_connection(), cursor.execute(...) e conn.commit() para localizar onde aplicar as alterações.



============================================================================
File: database.py
Line: 1
Type: potential_issue




============================================================================
File: tui.py
Line: 113 to 123
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 113 - 123, get_config currently leaks DB connections on exceptions and lacks type hints; add a return type annotation like -> Optional[Tuple[Any, ...]] (import Optional and Tuple) and ensure the connection and cursor are always closed by wrapping DB access in a try/finally (or use a context manager if self.db.get_connection() supports it): acquire conn via self.db.get_connection(), obtain cursor, execute and fetchone inside try, then in finally close cursor (if created) and conn, and return the fetched row (which may be None).



============================================================================
File: tui.py
Line: 235 to 286
Type: potential_issue




============================================================================
File: tui.py
Line: 190 to 233
Type: potential_issue

Prompt for AI Agent:
In @tui.py around lines 190 - 233, refresh_data currently swallows errors with bare except and a broad Exception handler and does naive duration math; change both exception handlers to catch only parsing-related errors (e.g. ValueError, TypeError) and log details via self.logger.exception or self.logger.error with context (reference refresh_data, self.db.get_active_users, self.db.get_recent_logs, table_active, table_logs), avoid catching SystemExit/KeyboardInterrupt; make timezone handling explicit by treating timestamps as timezone-aware when tzinfo is present and otherwise assigning a default timezone (e.g. UTC) before computing duration (use datetime.now(tz=ts.tzinfo) or datetime.now(timezone.utc) and normalize ts to that tz) so duration = now - ts is correct; keep the UI formatting (tipo_styled) but ensure error cases render an error indicator while logging the actual exception for debugging.



============================================================================
File: database.py
Line: 75 to 76
Type: potential_issue

Prompt for AI Agent:
In @database.py around lines 75 - 76, The commit and close calls use conn.commit() and conn.close() with no error handling; wrap the transaction so failures roll back and connections always close: either use a context manager (e.g., "with" or "async with aiosqlite.connect(...)" so the connection closes automatically) or surround the commit/close with try/except/finally, call conn.rollback() on exception, log the exception, and ensure conn.close() runs in finally; re-raise or return an error after logging as appropriate.



============================================================================
File: database.py
Line: 10 to 14
Type: potential_issue

Prompt for AI Agent:
In @database.py around lines 10 - 14, Refactor get_connection into an async factory with proper type hints and exception handling: change to async def get_connection(self) -> aiosqlite.Connection, open the DB with await aiosqlite.connect(self.db_path) inside a try/except catching aiosqlite.Error and re-raising or logging a clear message, apply the PRAGMA after connect (await conn.execute(...)) and return the connection; update callers to use "async with await self.get_connection()" (or better: provide an async contextmanager wrapper around get_connection) so connections are always closed and resources aren’t leaked.



============================================================================
File: database.py
Line: 1 to 3
Type: nitpick

Prompt for AI Agent:
In @database.py around lines 1 - 3, Remove the unused imports datetime and os from the top-level imports in this module; keep only the necessary import sqlite3 and ensure no other functions or classes (e.g., any DB connection or helper functions) rely on datetime/os before deleting them to avoid breaking references.



============================================================================
File: database.py
Line: 16 to 37
Type: potential_issue




============================================================================
File: database.py
Line: 6 to 8
Type: potential_issue

Prompt for AI Agent:
In @database.py around lines 6 - 8, The __init__ method on the Database class lacks type hints, a docstring, and never performs the promised validation; add a type hint for the db_path parameter and for the instance attribute (e.g., db_path: str), add a concise docstring explaining that __init__ sets the path and validates it, and call the existing (or newly added) validate_db_path(db_path: str) method from inside __init__ to enforce and raise on invalid paths; update references to self.db_path accordingly so the attribute has the declared type.



Review completed ✔
