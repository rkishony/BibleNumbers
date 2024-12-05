from typing import Dict, List

from bible_types import Verse, VerseAndNumericHebrews
from bible_types import NumericHebrew
from read_bible import clean_text
from verses_to_matches import load_or_create_verses_to_numerics
import matplotlib.pyplot as plt


def create_html_of_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews], file_name='verses_with_numbers.html'):
    html = "<html><head><meta charset='UTF-8'></head><body>"
    for verse_and_numeric_hebrews in verses_and_numeric_hebrews:
        verse_html = verse_and_numeric_hebrews.to_html()
        html += verse_html
    html += "</body></html>"
    with open(file_name, 'w') as file:
        file.write(html)


def print_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews]):
    for verse_and_numeric_hebrews in verses_and_numeric_hebrews:
        print(verse_and_numeric_hebrews)


def main():
    verses_to_matches = load_or_create_verses_to_numerics()
    verses_and_numeric_hebrews = []
    for verse, numeric_hebrews in verses_to_matches.items():
        verses_and_numeric_hebrews.append(VerseAndNumericHebrews(verse, numeric_hebrews))
    create_html_of_verses_with_numbers(verses_and_numeric_hebrews)
    print_verses_with_numbers(verses_and_numeric_hebrews)

    all_numbers = [numeric_hebrew.number for numeric_hebrews in verses_to_matches.values() for numeric_hebrew in numeric_hebrews]
    # plot accumulated histogram of all numbers
    all_numbers = sorted(all_numbers)
    plt.semilogx(all_numbers, range(len(all_numbers)), '.-')
    plt.show()


if __name__ == "__main__":
    main()
