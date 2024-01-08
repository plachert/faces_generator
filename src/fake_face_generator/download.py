import asyncio
import hashlib

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


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
@backoff.on_exception(backoff.expo, DuplicatedImageError, max_tries=None)
async def download_image(session, seen: set):
    async with session.get(url=URL) as response:
        if 200 <= response.status < 300:
            content = await response.read()
            hashed = hash_bytes(content)
            if hashed in seen:
                raise DuplicatedImageError
            filename = f"data/{len(seen)}.jpg"
            await save_image(content, filename)
            seen.add(hashed)
        else:
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                code=response.status,
                message=response.reason,
            )


async def save_image(bytes, filename):
    async with aiofiles.open(filename, "wb") as file:
        await file.write(bytes)


async def download_all():
    seen = set()
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, seen) for _ in range(10)]
        await asyncio.gather(*tasks)


async def main():
    await download_all()


if __name__ == "__main__":
    asyncio.run(main())
