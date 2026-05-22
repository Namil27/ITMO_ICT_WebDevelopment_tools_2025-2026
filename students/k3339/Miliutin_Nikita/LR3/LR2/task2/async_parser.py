import asyncio
import aiohttp
import aiosqlite
import time

from bs4 import BeautifulSoup


urls = [
    "https://example.com",
    "https://python.org",
    "https://github.com",
    "https://stackoverflow.com",
    "https://wikipedia.org",
    "https://docs.python.org",
    "https://pypi.org",
    "https://www.mozilla.org",
    "https://www.kernel.org",
    "https://archlinux.org",
    "https://www.debian.org",
    "https://www.ubuntu.com"
] * 10


async def parse_and_save(session, url):

    try:

        async with session.get(url) as response:

            html = await response.text()

            soup = BeautifulSoup(html, "html.parser")

            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            else:
                title = "No title"

            async with aiosqlite.connect("pages.db") as db:

                await db.execute(
                    "INSERT INTO pages (url, title) VALUES (?, ?)",
                    (url, title)
                )

                await db.commit()

            print(f"{url} -> {title}")

    except Exception as e:

        print(f"Error with {url}: {e}")


async def main():

    start_time = time.time()

    async with aiohttp.ClientSession() as session:

        tasks = []

        for url in urls:

            tasks.append(
                asyncio.create_task(
                    parse_and_save(session, url)
                )
            )

        await asyncio.gather(*tasks)

    end_time = time.time()

    print("Async time:", end_time - start_time)


asyncio.run(main())