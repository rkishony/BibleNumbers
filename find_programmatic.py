from typing import List

from bible_types import VerseAndNumericHebrews, NumericHebrew
from create_verses_html import create_html_of_verses_with_numbers
from programmatic_nikud import extract_number_phrases, hebrew_num_to_int, get_verses_with_numbers
from verses_to_matches import dump_verses_to_numerics


def extract_numeric_hebrews(verse) -> List[NumericHebrew]:
    number_phrases = extract_number_phrases(verse.text)

    return [NumericHebrew(
                book=verse.book,
                chapter=verse.chapter,
                letter=verse.letter,
                quote=phrase,
                number=hebrew_num_to_int(phrase),
                entity=''
    ) for phrase in number_phrases]


def main():
    verses = get_verses_with_numbers()
    verses_to_matches = {}
    for verse in verses:
        numeric_hebrews = extract_numeric_hebrews(verse)
        verses_to_matches[verse] = numeric_hebrews

    dump_verses_to_numerics('verses_to_numerics_p.json', verses_to_matches)

    verses_and_numeric_hebrews = []
    for verse, numeric_hebrews in verses_to_matches.items():
        verses_and_numeric_hebrews.append(VerseAndNumericHebrews(verse, numeric_hebrews))
    create_html_of_verses_with_numbers(verses_and_numeric_hebrews)


if __name__ == "__main__":
    main()
