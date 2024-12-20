import re

NIKUD_PATTERN = "[\u0590-\u05C7]*"  # Matches Hebrew vowel signs and diacritics


def remove_nikud(s):
    return re.sub(NIKUD_PATTERN, "", s)


def compare_without_nikud(s1, s2):
    return remove_nikud(s1) == remove_nikud(s2)

