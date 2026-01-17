# Database Optimization Notes

## 2024-05-23 - Database Connection & Indexing

**Learning:** Initializing database schema (CREATE TABLE IF NOT EXISTS) inside the class `__init__` method causes significant N+1 overhead (file I/O, locking) when the class is instantiated repeatedly for every command, even if tables already exist.

**Action:** Move schema initialization to an explicit `init_db()` method called once at application startup. Always check for missing indexes on filtering columns (WHERE clauses) as they can provide 50-100x speedups on SQLite.

## 2024-05-23 - Persistent Connection & Concurrency

**Learning:** Re-opening SQLite connections for every operation (N+1 connection problem) adds significant overhead (~60% of execution time). Switching to a persistent connection (`self.conn`) drastically improves throughput (2.6x faster). However, sharing a single `aiosqlite` connection across concurrent async tasks introduces race conditions and requires `asyncio.Lock()` around state-modifying transactions. Exception handlers must also explicitely call `rollback()` to prevent dirty state from affecting subsequent queries on the shared connection.

**Action:** When implementing persistent connections in `aiosqlite`, always initialize an `asyncio.Lock` and wrap transactions in `async with self.lock:`. Ensure `await self.conn.close()` is called on application shutdown.
