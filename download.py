import asyncio
import hashlib
import uuid

import aiofiles
import aiohttp
import backoff

URL = "https://thispersondoesnotexist.com"


class DuplicatedImageError(Exception):
    pass


def hash_bytes(bytes):
    hash = hashlib.md5()
    hash.update(bytes)
    return hash.hexdigest()


@backoff.on_exception(
    backoff.expo, (aiohttp.ClientError, DuplicatedImageError), max_tries=None
)
async def fetch_bytes(session, seen: set):
    try:
        async with session.get(url=URL) as response:
            if response.status == 200:
                content = await response.read()
                hashed = hash_bytes(content)
                if hashed in seen:
                    raise DuplicatedImageError
                filename = f"data/{uuid.uuid1()}.jpg"
                async with aiofiles.open(filename, "wb") as file:
                    await file.write(content)
                seen.add(hashed)
            else:
                print(f"Error: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Aiohttp error: {e}")
        raise


async def fetch_all():
    seen = set()
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_bytes(session, seen) for _ in range(10)]
        byte_responses = await asyncio.gather(*tasks)

        return byte_responses


async def main():
    await fetch_all()


if __name__ == "__main__":
    asyncio.run(main())
