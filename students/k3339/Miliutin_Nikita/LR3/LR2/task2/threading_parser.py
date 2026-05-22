import threading
import requests
import asyncio
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


async def save_to_db(url, title):

    async with aiosqlite.connect("pages.db") as db:

        await db.execute(
            "INSERT INTO pages (url, title) VALUES (?, ?)",
            (url, title)
        )

        await db.commit()


def parse_and_save(url):

    try:

        response = requests.get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        else:
            title = "No title"

        asyncio.run(save_to_db(url, title))

        print(f"{url} -> {title}")

    except Exception as e:

        print(f"Error with {url}: {e}")


threads = []

start_time = time.time()

for url in urls:

    thread = threading.Thread(
        target=parse_and_save,
        args=(url,)
    )

    threads.append(thread)

    thread.start()

for thread in threads:
    thread.join()

end_time = time.time()

print("Threading time:", end_time - start_time)