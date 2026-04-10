import random
import string
import time
from typing import Any

import requests


BASE_URL = "http://127.0.0.1:8000"

USERS_COUNT = 15
BOOKS_PER_USER = 4
EXCHANGE_REQUESTS_COUNT = 25

PASSWORD = "testpassword123"


FIRST_NAMES = [
    "Nikita", "Ivan", "Alexey", "Dmitry", "Anna",
    "Maria", "Elena", "Olga", "Sergey", "Pavel",
    "Andrey", "Maxim", "Kirill", "Artem", "Sofia",
]

LAST_NAMES = [
    "Ivanov", "Petrov", "Sidorov", "Smirnov", "Volkov",
    "Kuznetsov", "Popov", "Fedorov", "Orlov", "Mikhailov",
]

CITIES = [
    "Saint Petersburg", "Moscow", "Kazan", "Novosibirsk",
    "Yekaterinburg", "Samara", "Tomsk", "Perm",
]

BOOK_TITLES = [
    "1984", "Brave New World", "The Hobbit", "Dune", "Fahrenheit 451",
    "The Catcher in the Rye", "Crime and Punishment", "The Master and Margarita",
    "War and Peace", "The Little Prince", "Metro 2033", "Foundation",
    "Neuromancer", "The Witcher", "Harry Potter and the Philosopher's Stone",
]

AUTHORS = [
    "George Orwell", "Aldous Huxley", "J.R.R. Tolkien", "Frank Herbert",
    "Ray Bradbury", "J.D. Salinger", "Fyodor Dostoevsky", "Mikhail Bulgakov",
    "Leo Tolstoy", "Antoine de Saint-Exupery", "Dmitry Glukhovsky",
    "Isaac Asimov", "William Gibson", "Andrzej Sapkowski", "J.K. Rowling",
]

GENRES = [
    "Science Fiction", "Fantasy", "Classic", "Drama",
    "Adventure", "Dystopia", "Mystery",
]

CONDITIONS = [
    "new", "good", "used", "with notes",
]


def random_suffix(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def register_user(session: requests.Session, index: int) -> dict[str, Any] | None:
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    suffix = random_suffix()

    username = f"{first_name.lower()}_{last_name.lower()}_{suffix}"
    email = f"{username}@example.com"

    payload = {
        "email": email,
        "username": username,
        "password": PASSWORD,
        "full_name": f"{first_name} {last_name}",
        "city": random.choice(CITIES),
        "bio": f"Люблю читать книги и обмениваться ими. Пользователь #{index}",
    }

    response = session.post(f"{BASE_URL}/auth/register", json=payload)

    if response.status_code == 201:
        user = response.json()
        print(f"[OK] User created: id={user['id']} username={user['username']}")
        return user

    print(f"[ERROR] Failed to create user: {response.status_code} {response.text}")
    return None


def create_book(session: requests.Session, owner_id: int) -> dict[str, Any] | None:
    title_index = random.randrange(len(BOOK_TITLES))

    payload = {
        "title": f"{BOOK_TITLES[title_index]} ({random_suffix(3)})",
        "author": AUTHORS[title_index],
        "description": "Интересная книга для обмена.",
        "genre": random.choice(GENRES),
        "condition": random.choice(CONDITIONS),
    }

    response = session.post(
        f"{BASE_URL}/books/",
        params={"owner_id": owner_id},
        json=payload,
    )

    if response.status_code == 201:
        book = response.json()
        print(f"[OK] Book created: id={book['id']} owner_id={owner_id} title={book['title']}")
        return book

    print(f"[ERROR] Failed to create book for owner_id={owner_id}: {response.status_code} {response.text}")
    return None


def create_exchange_request(
    session: requests.Session,
    requester_id: int,
    book_id: int,
) -> dict[str, Any] | None:
    payload = {
        "book_id": book_id,
        "message": "Привет! Хочу обменяться этой книгой.",
    }

    response = session.post(
        f"{BASE_URL}/exchange-requests/",
        params={"requester_id": requester_id},
        json=payload,
    )

    if response.status_code == 201:
        exchange_request = response.json()
        print(
            f"[OK] Exchange request created: "
            f"id={exchange_request['id']} requester_id={requester_id} book_id={book_id}"
        )
        return exchange_request

    print(
        f"[WARN] Failed to create exchange request "
        f"(requester_id={requester_id}, book_id={book_id}): "
        f"{response.status_code} {response.text}"
    )
    return None


def main() -> None:
    session = requests.Session()

    try:
        health = session.get(f"{BASE_URL}/")
        health.raise_for_status()
    except requests.RequestException as exc:
        print(f"[FATAL] API is not available: {exc}")
        return

    users: list[dict[str, Any]] = []
    books: list[dict[str, Any]] = []

    print("=== Creating users ===")
    for i in range(USERS_COUNT):
        user = register_user(session, i + 1)
        if user:
            users.append(user)
        time.sleep(0.05)

    if len(users) < 2:
        print("[FATAL] Not enough users created.")
        return

    print("\n=== Creating books ===")
    for user in users:
        for _ in range(BOOKS_PER_USER):
            book = create_book(session, owner_id=user["id"])
            if book:
                books.append(book)
            time.sleep(0.05)

    if not books:
        print("[FATAL] No books created.")
        return

    print("\n=== Creating exchange requests ===")
    created_requests = 0
    attempts = 0
    max_attempts = EXCHANGE_REQUESTS_COUNT * 5

    while created_requests < EXCHANGE_REQUESTS_COUNT and attempts < max_attempts:
        attempts += 1

        book = random.choice(books)
        owner_id = book["owner_id"]

        possible_requesters = [user for user in users if user["id"] != owner_id]
        if not possible_requesters:
            continue

        requester = random.choice(possible_requesters)

        result = create_exchange_request(
            session=session,
            requester_id=requester["id"],
            book_id=book["id"],
        )

        if result:
            created_requests += 1

        time.sleep(0.05)

    print("\n=== Done ===")
    print(f"Users created: {len(users)}")
    print(f"Books created: {len(books)}")
    print(f"Exchange requests created: {created_requests}")


if __name__ == "__main__":
    main()