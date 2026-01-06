# Implementation Plan - Project Stabilization & Refactoring

## User Review Required

> **Critical**: This plan addresses 20+ issues identified in the CodeRabbit review
> (`analisecoderabbit_debug.md`). The changes involve core database logic, error handling, and
> Docker configuration.

## Proposed Changes

### Core: Database Stabilization (`src/database.py`)

#### [MODIFY] [src/database.py](file:///Users/gabrielramos/bots/ponto-salinha/src/database.py)

- **Error Handling**: Wrap all async methods in `try/except aiosqlite.Error`. Log errors with
  context and re-raise as a custom `DatabaseError`.
- **Logic Fixes**:
  - `register_entry`: Replace `INSERT OR REPLACE` with `SELECT` -> `INSERT/UPDATE` to prevent
    overwriting existing timestamps.
  - `register_exit`: Validate user state before insertion.
  - `clear_data`: safe handling of `total_changes`.
- **Validation**:
  - Add `validate_db_path` in `__init__`.
  - Validate `limit` regarding `MAX_LIMIT` in `get_user_records`.
  - Validate inputs in `set_config` (positive integers).

### Feature: Cogs Improvements (`src/cogs/*.py`)

#### [MODIFY] [src/cogs/ranking.py](file:///Users/gabrielramos/bots/ponto-salinha/src/cogs/ranking.py)

- **Timezone Fix**: Replace UTC usage with `ZoneInfo("America/Sao_Paulo")` for "Hoje", "Semana",
  "Mês" calculations.
- **UI Fix**: Map `periodo.capitalize()` to proper accented strings (e.g., "Mês").

#### [MODIFY] [src/cogs/ponto.py](file:///Users/gabrielramos/bots/ponto-salinha/src/cogs/ponto.py)

- **Audit Log**: Verify channel type (TextChannel) before sending logs.
- **Safety**: Handle `interaction.guild_id is None` (DMs).
- **Logic**: Clamp negative duration if `timestamp_entrada > now`.

#### [MODIFY] [src/cogs/admin.py](file:///Users/gabrielramos/bots/ponto-salinha/src/cogs/admin.py)

- **UX**: Add `ConfirmView` (Yes/No buttons) for `/limpar_dados`.
- **Error Handling**: Catch specific exceptions during config save.

#### [MODIFY] [src/cogs/report.py](file:///Users/gabrielramos/bots/ponto-salinha/src/cogs/report.py)

- **Async Fix**: Use `asyncio.get_running_loop()` instead of `get_event_loop()`.
- **Robustness**: Safe usage of `row.get()` and strict exception handling for cell value conversion.

### Infrastructure: Docker & Env (`Dockerfile`, `docker-compose.yml`, `README.md`)

#### [MODIFY] [Dockerfile](file:///Users/gabrielramos/bots/ponto-salinha/Dockerfile)

- **Persistence**: Add `VOLUME ["/app/data"]`.
- **Security**: Run as non-root user (`botuser`).
- **Permissions**: Fix ownership of copied files (`COPY --chown=botuser:botuser`).
- **Healthcheck**: Add `HEALTHCHECK` instruction.

#### [MODIFY] [docker-compose.yml](file:///Users/gabrielramos/bots/ponto-salinha/docker-compose.yml)

- **Healthcheck**: Define healthcheck definition for the service.
- **User**: explicit `user:` directive if needed.

#### [MODIFY] [README.md](file:///Users/gabrielramos/bots/ponto-salinha/README.md)

- **Documentation**: Add "Troubleshooting", "FAQ", and expanded "Access Control" sections.
- **Env**: Detail all `.env` variables.

#### [MODIFY] [.env.example](file:///Users/gabrielramos/bots/ponto-salinha/.env.example)

- **Clarification**: Add comments and English placeholders.

## Verification Plan

### Automated Verification

Since no test suite exists, I will create a basic sanity check script:

- `scripts/verify_db.py`: Tests connection and basic CRUD operations.

### Manual Verification

1. **Docker Build**: `docker build . -t ponto-salinha:test` (Check for build errors).
2. **Runtime**: Start bot with `docker-compose up`.
3. **Database**: Verify data persistence after container restart.
4. **Commands**:
   - `/ponto entrada` -> Check active status.
   - `/limpar_dados` -> Verify Confirmation View appears.
   - `/ranking` -> Verify Month/Year accents.
