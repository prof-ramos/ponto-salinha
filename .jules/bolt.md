# Database Optimization Notes

## 2024-05-23 - Database Connection & Indexing

**Learning:** Initializing database schema (CREATE TABLE IF NOT EXISTS) inside the class `__init__` method causes significant N+1 overhead (file I/O, locking) when the class is instantiated repeatedly for every command, even if tables already exist.

**Action:** Move schema initialization to an explicit `init_db()` method called once at application startup. Always check for missing indexes on filtering columns (WHERE clauses) as they can provide 50-100x speedups on SQLite.

## 2024-05-23 - Persistent Connection & Transaction Safety

**Learning:** Replacing per-operation `aiosqlite.connect` with a persistent connection significantly improved performance (~4.3x speedup). However, this removes the implicit rollback provided by the connection context manager on error.

**Action:** When using persistent connections, always implement explicit `await self.conn.rollback()` in exception handlers for write operations to prevent transaction leaks.
