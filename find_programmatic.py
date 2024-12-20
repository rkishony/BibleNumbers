from typing import List

from matplotlib import pyplot as plt

from bible_types import VerseAndNumericHebrews, NumericHebrew, Time
from create_verses_html import create_html_of_verses_with_numbers
from programmatic_nikud import extract_number_phrases, hebrew_num_to_int, get_verses_with_numbers


def extract_numeric_hebrews(verse) -> List[NumericHebrew]:
    number_phrases = extract_number_phrases(verse.text)
    numeric_hebrews = []
    for phrase in number_phrases:
        number = hebrew_num_to_int(phrase)
        numeric_hebrews.append(NumericHebrew(
            book=verse.book,
            chapter=verse.chapter,
            letter=verse.letter,
            quote=phrase,
            number=number,
            entity=''
        ))
    return numeric_hebrews

def _converrt_to_number(x):
    if isinstance(x, Time):
        try:
            return x.to_number()
        except:
            return None
    return x


def main():
    verses = get_verses_with_numbers()
    verses_to_matches = {}
    for verse in verses:
        numeric_hebrews = extract_numeric_hebrews(verse)
        verses_to_matches[verse] = numeric_hebrews

    # dump_verses_to_numerics('verses_to_numerics_p.json', verses_to_matches)

    verses_and_numeric_hebrews = []
    for verse, numeric_hebrews in verses_to_matches.items():
        verses_and_numeric_hebrews.append(VerseAndNumericHebrews(verse, numeric_hebrews))
    create_html_of_verses_with_numbers(verses_and_numeric_hebrews)

    total_numeric_hebrews = 0
    for verse, numeric_hebrews in verses_to_matches.items():
        total_numeric_hebrews += len(numeric_hebrews)
    print(f"Total numeric hebrews: {total_numeric_hebrews}")

    all_numbers = [_converrt_to_number(numeric_hebrew.number) for numeric_hebrews in verses_to_matches.values() for numeric_hebrew in numeric_hebrews]
    # plot accumulated histogram of all numbers
    all_numbers = sorted(all_numbers)
    plt.semilogx(all_numbers, range(len(all_numbers)), '.-')
    plt.show()


if __name__ == "__main__":
    main()
