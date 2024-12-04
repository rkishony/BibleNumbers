from typing import Dict, List

from bible_types import Verse
from bible_types import NumericHebrew
from read_bible import clean_text
from verses_to_matches import load_or_create_verses_to_numerics
import matplotlib.pyplot as plt


def print_verse_with_numbers(verse, numeric_hebrews):
    """
    print the verse in black.
    for each numeric_hebrew that is in the verse, print it in red, and add the number in green right after it.
    """
    text = verse.text
    for numeric_hebrew in numeric_hebrews:
        quote = clean_text(numeric_hebrew.quote)
        number = numeric_hebrew.number
        entity = numeric_hebrew.entity
        text = text.replace(quote, f"\033[31m{quote}\033[0m\033[32m [{number} {entity}]\033[0m")
    color_marks_len = 9 * 2
    len_text = len(text) - len(numeric_hebrews) * color_marks_len
    text = " " * (180 - len_text) + text
    print(text)


def verse_with_numbers_to_html(verse, numeric_hebrews):
    text = verse.text
    for numeric_hebrew in numeric_hebrews:
        quote = clean_text(numeric_hebrew.quote)
        number = numeric_hebrew.number
        entity = numeric_hebrew.entity
        text = text.replace(quote, f"<span style='color:red'>{quote}</span><span style='color:green'> [{number} {entity}]</span>")
    return text


def create_html_of_verses_with_numbers(verses_to_matches: Dict[Verse, List[NumericHebrew]], file_name: str = "verses_with_numbers.html"):
    html = "<html><head><meta charset='UTF-8'></head><body>"
    for verse, numeric_hebrews in verses_to_matches.items():
        # need RTL for Hebrew:
        html += f"<div dir='rtl'>{verse_with_numbers_to_html(verse, numeric_hebrews)}</div><br>"
    html += "</body></html>"
    with open(file_name, 'w') as file:
        file.write(html)


def main():
    verses_to_matches = load_or_create_verses_to_numerics()
    for verse, numeric_hebrews in verses_to_matches.items():
        print_verse_with_numbers(verse, numeric_hebrews)
    create_html_of_verses_with_numbers(verses_to_matches)
    all_numbers = [numeric_hebrew.number for numeric_hebrews in verses_to_matches.values() for numeric_hebrew in numeric_hebrews]
    # plot accumulated histogram of all numbers
    all_numbers = sorted(all_numbers)
    plt.semilogx(all_numbers, range(len(all_numbers)),'.-')
    plt.show()





if __name__ == "__main__":
    main()
