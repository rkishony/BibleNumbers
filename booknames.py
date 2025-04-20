from typing import List

BOOK_NAMES = None


def get_book_names() -> List[str]:
    global BOOK_NAMES
    if BOOK_NAMES is None:
        books_folder = "bible_book_names.txt"
        with open(books_folder, "r", encoding="utf-8") as file:
            book_names = file.readlines()
        BOOK_NAMES = [name.strip() for name in book_names if name.strip()]
    return BOOK_NAMES


def get_book_num(book_name: str) -> int:
    book_names = get_book_names()
    return book_names.index(book_name) + 1
