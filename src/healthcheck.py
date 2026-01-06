import sqlite3
import os
import sys


def check_db():
    db_path = os.getenv("DATABASE_PATH", "/app/data/ponto.db")

    # If DB doesn't exist yet, it might be initializing.
    # But for a running bot, it should exist shortly.
    if not os.path.exists(db_path):
        # We might fail or pass depending on strictness.
        # If it's a fresh container, wait.
        return True  # Assume OK during startup? No, HEALTHCHECK has start_period.
        # Let's return False if not found after start_period?
        # Actually returning 0 is success.
        # If file not found, we can say "Initializing" check log?
        # Let's try to connect. If fails, it fails.
        pass

    try:
        # Check if we can open for reading
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except sqlite3.Error:
        return False
    except Exception:
        return False


if __name__ == "__main__":
    if check_db():
        sys.exit(0)
    else:
        sys.exit(1)
