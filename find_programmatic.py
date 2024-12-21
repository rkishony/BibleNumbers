import numpy as np
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


def plot_accumulated_histogram(ax, x, normalize=False, marker='o', linestyle='-', color='b', name=''):
    x = sorted(x)
    y = np.arange(len(x))
    if normalize:
        y = y / y[-1]
    name += f' (n={len(x)})'
    ax.semilogx(x, y, marker=marker, linestyle=linestyle, color=color, markersize=2, label=name)


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

    all_numeric_hebrews = [numeric_hebrew for numeric_hebrews in verses_to_matches.values() for numeric_hebrew in numeric_hebrews]

    not_time = [x.number for x in all_numeric_hebrews if not isinstance(x.number, Time)]

    all_numbers = [_converrt_to_number(numeric_hebrew.number) for numeric_hebrew in all_numeric_hebrews]

    all_years = [x.number.to_number() for x in all_numeric_hebrews if isinstance(x.number, Time)]

    # plot accumulated histogram of all numbers
    # plt.figure()
    # ax = plt.gca()
    # plot_accumulated_histogram(ax, all_numbers, normalize=True, color='r', name='All numbers')
    # plot_accumulated_histogram(ax, all_years, normalize=True, color='g', name='All years')
    # plot_accumulated_histogram(ax, not_time, normalize=True, color='b', name='Not time')
    # ax.legend()
    # ax.set_xlabel('Value')
    # ax.set_ylabel('Accumulated fraction')
    # plt.show()


if __name__ == "__main__":
    main()
