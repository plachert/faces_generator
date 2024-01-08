import aiohttp
import asyncio
import aiofiles
import backoff
import uuid
import hashlib


URL = "https://thispersondoesnotexist.com"


class DuplicatedImageError(Exception):
    pass


def hash_bytes(bytes):
    hash = hashlib.md5()
    hash.update(bytes)
    return hash.hexdigest()


seen = set()

@backoff.on_exception(backoff.expo, (aiohttp.ClientError, DuplicatedImageError), max_tries=None)
async def fetch_bytes(session):
    try:
        async with session.get(url=URL) as response:
            if response.status == 200:
                content = await response.read()
                hashed = hash_bytes(content)
                if hashed in seen:
                    raise DuplicatedImageError
                filename = f"data/{uuid.uuid1()}.jpg"
                async with aiofiles.open(filename, 'wb') as file:
                    await file.write(content)
                seen.add(hashed)
            else:
                print(f"Error: {response.status}")
    except aiohttp.ClientError as e:
        print(f"Aiohttp error: {e}")
        raise


async def fetch_all():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_bytes(session) for _ in range(10)]
        byte_responses = await asyncio.gather(*tasks)

        return byte_responses

async def main():
    await fetch_all()

if __name__ == "__main__":
    asyncio.run(main())
