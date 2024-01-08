import asyncio
import hashlib
import pathlib

import aiofiles
import aiohttp
import backoff
from tqdm.asyncio import tqdm_asyncio

URL = "https://thispersondoesnotexist.com"


class DuplicatedImageError(Exception):
    pass


def hash_bytes(bytes):
    hash = hashlib.md5()
    hash.update(bytes)
    return hash.hexdigest()


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
@backoff.on_exception(backoff.expo, DuplicatedImageError, max_tries=None)
async def download_image(
    session: aiohttp.ClientSession,
    seen: set,
    data_dir: pathlib.Path,
):
    async with session.get(url=URL) as response:
        if 200 <= response.status < 300:
            content = await response.read()
            hashed = hash_bytes(content)
            if hashed in seen:
                raise DuplicatedImageError
            filename = data_dir / f"{len(seen) + 1}.jpg"
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
    data_dir = pathlib.Path("data")
    n = 10
    seen = set()
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, seen, data_dir) for _ in range(n)]
        await tqdm_asyncio.gather(*tasks, desc="Downloading fake images")


async def main():
    await download_all()


if __name__ == "__main__":
    asyncio.run(main())
