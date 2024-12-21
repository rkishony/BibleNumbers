from matplotlib import pyplot as plt

from bible_types import VerseAndNumericHebrews, Time
from create_verses_html import create_html_of_verses_with_numbers, create_text_of_verses_with_numbers
from programmatic_nikud import get_verses_with_numbers, GetHebrewNumbers


def _converrt_to_number(x):
    if isinstance(x, Time):
        try:
            return x.to_number()
        except:
            return None
    return x


def main():
    verses = get_verses_with_numbers(with_nikud=True, remove_punctuations=False)
    verses_to_matches = {}
    for verse in verses:
        # numeric_hebrews = extract_numeric_hebrews(verse)
        numeric_hebrews = GetHebrewNumbers(verse.text).get()
        verses_to_matches[verse] = numeric_hebrews

    # dump_verses_to_numerics('verses_to_numerics_p.json', verses_to_matches)

    verses_and_numeric_hebrews = []
    for verse, numeric_hebrews in verses_to_matches.items():
        verses_and_numeric_hebrews.append(VerseAndNumericHebrews(verse, numeric_hebrews))
    create_html_of_verses_with_numbers(verses_and_numeric_hebrews)
    create_text_of_verses_with_numbers(verses_and_numeric_hebrews)

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
