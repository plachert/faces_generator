import asyncio
import hashlib
import pathlib
import pickle
import uuid

import aiofiles
import aiohttp
import backoff
from tqdm.asyncio import tqdm_asyncio

URL = "https://thispersondoesnotexist.com"
CONCURRENT_LIMIT = 50
SEEN_FILENAME = "seen_images.pkl"


class DuplicatedImageError(Exception):
    pass


def hash_bytes(content: bytes):
    """
    Generate an MD5 hash for the given bytes.

    Args:
        bytes: The input bytes to be hashed.

    Returns:
        str: The hexadecimal representation of the MD5 hash.
    """
    hash = hashlib.md5()
    hash.update(content)
    return hash.hexdigest()


@backoff.on_exception(
    backoff.expo, aiohttp.ClientError, max_tries=3, factor=2, jitter=backoff.full_jitter
)
@backoff.on_exception(backoff.expo, DuplicatedImageError, max_tries=None)
async def download_image(
    session: aiohttp.ClientSession,
    seen: set,
    data_dir: pathlib.Path,
    lock: asyncio.Lock,
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
            async with lock:
                if hashed in seen:
                    raise DuplicatedImageError
                filename = data_dir / f"{uuid.uuid4()}.jpg"
                await save_image(content, filename)
                seen.add(hashed)
        else:
            raise aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                code=response.status,
                message=response.reason,
            )


async def save_image(image: bytes, filename: pathlib.Path):
    """
    Save the given bytes to a file.

    Args:
        image: Image to be saved.
        filename (pathlib.Path): The path where the file will be saved.

    Returns:
        None
    """
    async with aiofiles.open(filename, "wb") as file:
        await file.write(image)


async def download_all_images(data_dir: pathlib.Path, n_images: int, seen: set):
    """
    Download a specified number of unique images concurrently.

    Args:
        data_dir (pathlib.Path): The directory where images will be saved.
        n_images (int): The number of unique images to be generated.
        seen (set): Set for tracking unique images

    Returns:
        None
    """
    lock = asyncio.Lock()
    semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=120)
    ) as session:

        async def download_with_semaphore():
            async with semaphore:
                await download_image(session, seen, data_dir, lock)

        tasks = [download_with_semaphore() for _ in range(n_images)]
        await tqdm_asyncio.gather(*tasks, desc="Downloading fake images")
    seen_file = data_dir / SEEN_FILENAME
    with open(seen_file, "wb") as f:
        pickle.dump(seen, f)


def run(data_dir: pathlib.Path, n_images: int):
    seen_file = data_dir / SEEN_FILENAME
    if seen_file.exists():
        with open(seen_file, "rb") as f:
            seen = pickle.load(f)
    else:
        seen = set()
    data_dir.mkdir(parents=True, exist_ok=True)
    asyncio.run(download_all_images(data_dir, n_images, seen))
