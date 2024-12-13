import re
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup

from bible_types import Verse, Verses

ROOT_DIRECTORY = Path(__file__).parent

BIBLES = dict()


def get_all_html_files(boos_dir: str) -> List[str]:
    books_folder = ROOT_DIRECTORY / boos_dir
    return sorted([str(file) for file in books_folder.glob("*.htm")])


def get_html(file_name: str) -> str:
    with open(file_name, "r", encoding="windows-1255", errors="ignore") as file:
        return file.read()


def clean_text(s):
    s = s.strip()
    # Replace hyphens with spaces
    s = s.replace('-', ' ')
    # Include letters or Hebrew vowels/nikud
    pattern = r'[\u05D0-\u05EA\u0590-\u05C7 {}]'
    # Use re.findall to keep only the matched characters
    cleaned_string = ''.join(re.findall(pattern, s))
    # Replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    return cleaned_string


def get_book_from_html(html_content: str, remove_punctuations: bool = True) -> Verses:
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
            if remove_punctuations:
                verse_text = clean_text(verse_text)
            verses.append(Verse(book_name, chapter_number, verse_number, verse_text))

    return verses


def get_bible(with_nikud: bool = False, remove_punctuations: bool = True) -> Verses:
    if with_nikud:
        name = "books_nikud"
    else:
        name = "books_maleh"

    if name not in BIBLES:
        verse = []
        for file_name in get_all_html_files(name):
            html = get_html(file_name)
            book = get_book_from_html(html, remove_punctuations)
            verse.extend(book)

        BIBLES[name] = verse

    return BIBLES[name]


def get_bible_as_one_text(with_nikud: bool = False) -> str:
    return '\n'.join([verse.text for verse in get_bible(with_nikud)])

def find_all_verses_containing(phrase: str, with_nikud: bool = False, remove_punctuations: bool = True) -> List[Verse]:
    verses = get_bible(with_nikud, remove_punctuations)
    return [verse for verse in verses if phrase in verse.text]


s = "שְׁנֵים"
for v in find_all_verses_containing(s, with_nikud=True, remove_punctuations=False):
    print(v.text)
