import asyncio
import sys
import os
import time
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from database import Database

# Configure logging to avoid spam
logging.basicConfig(level=logging.ERROR)

async def main():
    # Setup test DB
    db_path = "test_benchmark.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    # Initialize DB
    db = Database(db_path=db_path)
    await db.init_db()

    # Insert config
    guild_id = 123456789
    await db.set_config(guild_id, 987654321, 111222333)

    # Benchmark get_config
    iterations = 1000
    start_time = time.time()

    for _ in range(iterations):
        await db.get_config(guild_id)

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = (total_time / iterations) * 1000 # ms

    print(f"Total time for {iterations} calls: {total_time:.4f}s")
    print(f"Average time per call: {avg_time:.4f}ms")

    # Verify Invalidation
    print("Verifying invalidation...")
    await db.set_config(guild_id, 555555, 666666)

    # The next call should be slow(er) because it hits DB?
    # Actually, the file I/O is fast, but it should fetch from DB.
    # We can check if the value returned is the new one.

    config = await db.get_config(guild_id)
    if config['log_channel_id'] == 555555:
        print("Invalidation successful: Config updated.")
    else:
        print(f"Invalidation FAILED: Got {config['log_channel_id']}")

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    asyncio.run(main())
