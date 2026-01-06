# Database Optimization Notes

## 2024-05-23 - Database Connection & Indexing

**Learning:** Initializing database schema (CREATE TABLE IF NOT EXISTS) inside the class `__init__` method causes significant N+1 overhead (file I/O, locking) when the class is instantiated repeatedly for every command, even if tables already exist.

**Action:** Move schema initialization to an explicit `init_db()` method called once at application startup. Always check for missing indexes on filtering columns (WHERE clauses) as they can provide 50-100x speedups on SQLite.
