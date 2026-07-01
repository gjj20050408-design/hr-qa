import asyncio
from app.core.database import engine
from app.core.config import settings
from sqlalchemy import text

async def main():
    print("DB =", settings.DB_HOST, settings.DB_PORT, settings.DB_NAME)
    async with engine.connect() as c:
        for t in ['users', 'categories', 'documents']:
            r = await c.execute(text(f'SELECT COUNT(*) FROM {t}'))
            print(t, '=', r.scalar())
        r = await c.execute(text('SELECT status, COUNT(*) FROM documents GROUP BY status'))
        print('doc status:', r.fetchall())
    await engine.dispose()

asyncio.run(main())
