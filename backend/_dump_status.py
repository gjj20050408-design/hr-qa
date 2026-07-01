import asyncio
from app.core.database import engine
from sqlalchemy import text

async def main():
    async with engine.connect() as c:
        r = await c.execute(text("SELECT document_id, title, status, HEX(status) FROM documents"))
        for row in r.fetchall():
            print(repr(row[1])[:20], '| status=', repr(row[2]), '| hex=', row[3])
    await engine.dispose()

asyncio.run(main())
