from typing import Optional

from bible_types import Verses
from read_bible import BIBLE_MALE


def search_in_bible(quote: str, verses: Verses = BIBLE_MALE, expected: Optional[int] = None) -> Verses:
    """
    Search for a quote in the Bible and return the verses that contain it.
    """
    verses = [verse for verse in verses if quote in verse.text]
    if expected is not None and len(verses) != expected:
        raise ValueError(f"Expected {expected} verses, but found {len(verses)}")
    return verses
