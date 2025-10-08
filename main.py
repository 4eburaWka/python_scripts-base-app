import asyncio
from cache.redis import redis_set


async def main():
    await redis_set("e", 3)

asyncio.run(main())