import pickle
from pathlib import Path
from typing import List, Tuple

from bs4 import BeautifulSoup

from bible_types import Verse, Verses

ROOT_DIRECTORY = Path(__file__).parent
BOOKS_DIRECTORY = ROOT_DIRECTORY / "books"


def get_all_html_files() -> List[str]:
    return sorted([str(file) for file in BOOKS_DIRECTORY.glob("*.htm")])


def get_html(file_name: str) -> str:
    with open(file_name, "r", encoding="windows-1255") as file:
        return file.read()


def clean_text(s):
    s = s.strip()
    for char in ['-', '\n', '\r', '\t', '־', '  ']:
        s = s.replace(char, ' ')
    s = ''.join([c for c in s if 'א' <= c <= 'ת' or c == ' '])
    return s


def get_book_from_html(html_content: str) -> Verses:
    soup = BeautifulSoup(html_content, "html.parser")
    book_name = soup.find("h1").get_text(strip=True)
    if book_name == "תורה נביאים וכתובים":
        book_name = "בראשית"  # fix the name of the first book
    verse_paragraphs = soup.find_all("p")
    verses = []
    for paragraph in verse_paragraphs:
        # Each verse starts with <B> (bold) containing the verse number
        bold_elements = paragraph.find_all("b")
        for bold_element in bold_elements:
            chapter_and_verse = bold_element.get_text(strip=True)
            chapter_number, verse_number = chapter_and_verse.split(",")
            verse_text = bold_element.find_next_sibling(string=True)
            verse_text = clean_text(verse_text)
            verses.append(Verse(book_name, chapter_number, verse_number, verse_text))

    return verses


def get_bible() -> Verses:
    verse = []
    for file_name in get_all_html_files():
        html = get_html(file_name)
        book = get_book_from_html(html)
        verse.extend(book)
    return verse


BIBLE = get_bible()
