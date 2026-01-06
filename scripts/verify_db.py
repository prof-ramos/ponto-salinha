import asyncio
import os
import sys

# Add src to path to import database module
sys.path.append(os.path.join(os.getcwd(), "src"))

from database import Database


async def test_db():
    print("Testing Database...")
    db_file = "test_ponto.db"
    try:
        if os.path.exists(db_file):
            os.remove(db_file)

        db = Database(db_path=db_file)
        await db.init_db()
        print("✅ Init DB")

        # Test Config
        await db.set_config(123, 456)
        cfg = await db.get_config(123)
        assert cfg["log_channel_id"] == 456
        print("✅ Config CRUD")

        # Test Entry
        from datetime import datetime

        now = datetime.now().isoformat()
        await db.register_entry(1, 123, now)
        status = await db.get_user_status(1, 123)
        assert status["status"] == "ativo"
        print("✅ Entry Registration")

        # Test Exit
        await db.register_exit(1, 123, now, 3600)
        status = await db.get_user_status(1, 123)
        # We expect status to be 'inativo' or record updated.
        # Actually register_exit sets status='inativo'
        # status query returns a row?
        status_row = await db.get_user_status(1, 123)
        assert status_row["status"] == "inativo"

        # Check records
        recs = await db.get_user_records(1, 123)
        assert len(recs) == 2  # entry + exit
        print("✅ Exit Registration")

        print("🎉 Database verification passed!")
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if os.path.exists(db_file):
            os.remove(db_file)


if __name__ == "__main__":
    asyncio.run(test_db())
