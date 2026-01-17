import asyncio
import time
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from database import Database  # noqa: E402


async def benchmark():
    db_path = "benchmark.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = Database(db_path=db_path)
    await db.init_db()

    start_time = time.time()

    guild_id = 123456789
    user_id = 987654321

    # Simulate 100 operations (mix of writes and reads)
    print("Starting benchmark with 100 iterations...")
    for i in range(100):
        # Write config
        await db.set_config(guild_id, 111222333)

        # Read config
        await db.get_config(guild_id)

        # Register Entry
        timestamp = f"2024-01-01T10:{i % 60:02d}:00"
        await db.register_entry(user_id, guild_id, timestamp)

        # Get Status
        await db.get_user_status(user_id, guild_id)

        # Register Exit
        timestamp_exit = f"2024-01-01T18:{i % 60:02d}:00"
        await db.register_exit(user_id, guild_id, timestamp_exit, 28800)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Benchmark completed in {duration:.4f} seconds")
    print(f"Average time per iteration (5 ops): {duration / 100:.4f} seconds")

    await db.close()

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    asyncio.run(benchmark())
