from __future__ import annotations
import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bible_types import Verses


def search_in_bible(quote: str, verses: Verses, expected: Optional[int] = None) -> Verses:
    """
    Search for a quote in the Bible and return the verses that contain it.
    """
    verses = [verse for verse in verses if quote in verse.text]
    if expected is not None and len(verses) != expected:
        raise ValueError(f"Expected {expected} verses, but found {len(verses)}")
    return verses


def tokenize_words_and_punctuations(s) -> list[tuple[bool, str]]:
    # Define the regex for Hebrew words with niqqud
    word_pattern = r'[\u0590-\u05FF]+'

    # Split the text into words and separators
    split_parts = re.split(f'({word_pattern})', s)

    # Tag each part as a word or a separator
    tokenized = [
        (True, part) if re.fullmatch(word_pattern, part) else (False, part)
        for part in split_parts if part != ""
    ]

    # assert that word in even index and separator in odd index:
    for i, (is_word, _) in enumerate(tokenized):
        if i % 2 == 0:
            assert is_word
        else:
            assert not is_word

    return tokenized


def reconstruct(tokens):
    # Reconstruct the sentence from the tokenized parts
    return ''.join(part for _, part in tokens)


