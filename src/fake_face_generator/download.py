import argparse
import asyncio
import hashlib
import pathlib

import aiofiles
import aiohttp
import backoff
from tqdm.asyncio import tqdm_asyncio

URL = "https://thispersondoesnotexist.com"
CONCURRENT_LIMIT = 50


class DuplicatedImageError(Exception):
    pass


def hash_bytes(bytes):
    """
    Generate an MD5 hash for the given bytes.

    Args:
        bytes: The input bytes to be hashed.

    Returns:
        str: The hexadecimal representation of the MD5 hash.
    """
    hash = hashlib.md5()
    hash.update(bytes)
    return hash.hexdigest()


@backoff.on_exception(
    backoff.expo, aiohttp.ClientError, max_tries=3, factor=2, jitter=backoff.full_jitter
)
@backoff.on_exception(backoff.expo, DuplicatedImageError, max_tries=None)
async def download_image(
    session: aiohttp.ClientSession,
    seen: set,
    data_dir: pathlib.Path,
):
    """
    Download an image and save it if it's unique.

    Args:
        session (aiohttp.ClientSession): The aiohttp session for making HTTP requests.
        seen (set): A set containing hashes of previously downloaded images.
        data_dir (pathlib.Path): The directory where images will be saved.

    Raises:
        aiohttp.ClientResponseError: If the HTTP response status code is not in the 2xx range.
        DuplicatedImageError: If the downloaded image is a duplicate.

    Returns:
        None
    """
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
    """
    Save the given bytes to a file.

    Args:
        bytes: The bytes to be saved.
        filename (pathlib.Path): The path where the file will be saved.

    Returns:
        None
    """
    async with aiofiles.open(filename, "wb") as file:
        await file.write(bytes)


async def download_all_images(data_dir: pathlib.Path, n_images: int):
    """
    Download a specified number of unique images concurrently.

    Args:
        data_dir (pathlib.Path): The directory where images will be saved.
        n_images (int): The number of unique images to be generated.

    Returns:
        None
    """
    seen = set()
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=120)
    ) as session:

        async def download_with_semaphore():
            async with semaphore:
                await download_image(session, seen, data_dir)

        tasks = [download_with_semaphore() for _ in range(n_images)]
        await tqdm_asyncio.gather(*tasks, desc="Downloading fake images")


async def main(args):
    data_dir = pathlib.Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    n_images = args.n_images
    await download_all_images(data_dir, n_images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download unique images from thispersondoesnotexist.com"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        help="Path to the directory where you'd like to store the images.",
        required=True,
    )
    parser.add_argument(
        "--n_images",
        type=int,
        help="Number of unique images to be generated.",
        required=True,
    )
    args = parser.parse_args()
    asyncio.run(main(args))
