
import asyncio
import aiosqlite


async def create_db():

    async with aiosqlite.connect("pages.db") as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT
        )
        """)

        await db.commit()

        print("Database created")


asyncio.run(create_db())