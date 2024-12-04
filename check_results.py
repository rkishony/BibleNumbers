import numpy as np

from read_bible import clean_text
from verses_to_matches import load_or_create_verses_to_numerics
from view import print_verse_with_numbers


def check_multi_match(verse, numeric_hebrews):
    for numeric_hebrew in numeric_hebrews:
        quote = clean_text(numeric_hebrew.quote)
        if verse.text.count(quote) != 1:
            return False
    return True


def check_overlapping_matches(verse, numeric_hebrews):
    coverage = np.zeros(len(verse.text), dtype=int)
    for numeric_hebrew in numeric_hebrews:
        quote = clean_text(numeric_hebrew.quote)
        start = verse.text.find(quote)
        end = start + len(quote)
        coverage[start:end] += 1
    return np.all(coverage <= 1)


verses_to_matches = load_or_create_verses_to_numerics()
for verse, numeric_hebrews in verses_to_matches.items():
    if not check_overlapping_matches(verse, numeric_hebrews):
        print_verse_with_numbers(verse, numeric_hebrews)
