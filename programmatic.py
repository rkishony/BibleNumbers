from enum import Enum
from typing import Optional

from read_bible import get_bible

UNITS_MAP = {
    'אחת': 1, 'אחד': 1,
    'שתיים': 2, 'שתי': 2, 'שניים': 2, 'שני': 2,
    'שלוש': 3, 'שלושה': 3,
    'ארבע': 4, 'ארבעה': 4,
    'חמש': 5, 'חמישה': 5,
    'שש': 6, 'שישה': 6,
    'שבע': 7, 'שבעה': 7,
    'שמונה': 8,
    'תשע': 9, 'תשעה': 9,

    # Construct forms:
    'שלושת': 3,
    'ארבעת': 4,
    'חמשת': 5,
    'ששת': 6,
    'שבעת': 7,
    'שמונת': 8,
    'תשעת': 9,

    # Conjunctive forms:
    'שתים': 2,
}

TENS_MAP = {
    'עשר': 10, 'עשרה': 10,
    'עשרים': 20,
    'שלושים': 30,
    'ארבעים': 40,
    'חמישים': 50,
    'שישים': 60,
    'שבעים': 70,
    'שמונים': 80,
    'תשעים': 90
}

UNITS_AND_TENS_MAP = UNITS_MAP | TENS_MAP

HUNDREDS_MAP = {
    'מאה': 100, 'מאת': 100,
    'מאתיים': 200
}

THOUSANDS_MAP = {
    'אלף': 1000,
    'אלפיים': 2000
}

TENTHOUSANDS_MAP = {
    'רבבה': 10000,
    'ריבוא': 10000
}

PLURAL_MAP = {
    'מאות': 100,
    'אלפים': 1000,
    'רבבות': 10000
}

ALL_PLURAL_MAP = PLURAL_MAP | TENTHOUSANDS_MAP | THOUSANDS_MAP


ALL_NUMBER_WORDS = set(UNITS_AND_TENS_MAP) | set(HUNDREDS_MAP) | set(ALL_PLURAL_MAP)


IGNORE_WORDS = {"שנה", "שנות", "שנים", "חודש", "חודשים"}


class ConjugateLetter(Enum):
    """Conjugate letters for numbers."""
    BET = 'ב'
    VAV = 'ו'
    HEY = 'ה'


def preprocess_token(token: str) -> tuple[str, Optional[ConjugateLetter]]:
    """Preprocess token to identify if it's a conjunction and remove leading 'ו'."""
    for letter in ConjugateLetter:
        if token.startswith(letter.value):
            return token[1:], letter
    return token, None


def hebrew_num_to_int(phrase: str) -> int:

    tokens = phrase.split()

    total = 0
    current_segment = 0
    segment_parts = []  # track numbers added in the current segment

    def add_number(num, conjugate_letter):
        nonlocal current_segment, segment_parts
        if conjugate_letter:
            current_segment += num
            segment_parts.append(num)
        else:
            if current_segment == 0:
                current_segment = num
                segment_parts = [num]
            else:
                # Add it (rare case without 'ו'), but let's keep consistency
                current_segment += num
                segment_parts.append(num)

    def multiply_last(factor):
        nonlocal current_segment, segment_parts
        if not segment_parts:
            # If no parts, just add factor
            current_segment += factor
            segment_parts.append(factor)
        else:
            last = segment_parts.pop()
            new_val = last * factor
            current_segment = current_segment - last + new_val
            segment_parts.append(new_val)

    for token in tokens:
        token, conjugate_letter = preprocess_token(token)

        if token in IGNORE_WORDS:
            continue

        # Units or construct forms
        if token in UNITS_AND_TENS_MAP:
            add_number(UNITS_AND_TENS_MAP[token], conjugate_letter)
            continue

        # Hundreds
        if token in HUNDREDS_MAP:
            val = HUNDREDS_MAP[token]
            if conjugate_letter:
                # Add 100 or 200
                current_segment += val
                segment_parts.append(val)
            else:
                # Multiply last number by 100 or add 200 if it makes sense
                if val == 100:
                    multiply_last(100)
                else:
                    # val == 200 (מאתיים)
                    # Typically means just 200. If we have a previous number and no 'ו', it's tricky.
                    # We'll treat "מאתיים" like a standalone 200 if no conjunction.
                    if len(segment_parts) == 1 and segment_parts[0] != 0:
                        # Not a standard form, but let's just add 200
                        current_segment += 200
                        segment_parts.append(200)
                    else:
                        current_segment += 200
                        segment_parts.append(200)
            continue

        if token in ALL_PLURAL_MAP:
            value = ALL_PLURAL_MAP[token]
            if conjugate_letter:
                current_segment += value
                segment_parts.append(value)
            else:
                multiply_last(value)
            continue

        # token not recognized as number, we can continue or raise an error
        continue

    total += current_segment
    return total


def iter_hebrew_numbers(with_hatayot: bool = True):
    for unit in ALL_NUMBER_WORDS:
        yield unit
        # add ו
        yield f"ו{unit}"


def is_word_in_hebrew_numbers(word: str) -> bool:
    return word in iter_hebrew_numbers()


def is_numbers_in_verse(verse) -> bool:
    return any(is_word_in_hebrew_numbers(word) for word in verse.split(' '))


def extract_number_phrases(verse: str) -> list[str]:

    tokens = verse.split()
    phrases = []
    current_phrase = []

    def terminate_phrase():
        if current_phrase:
            phrases.append(" ".join(current_phrase))
            current_phrase.clear()

    for i, raw_token in enumerate(tokens):
        # Preprocess token to identify if it's conjunction and remove leading 'ו'
        token, conjugate_letter = preprocess_token(raw_token)
        # Check if token is a number word or in the ignore words
        if token in ALL_NUMBER_WORDS:
            # if conjugate_letter in {ConjugateLetter.BET, ConjugateLetter.HEY}:
            #     terminate_phrase()
            # Start or continue a phrase
            current_phrase.append(raw_token)
            # terminate if end of sentence, or for שנים שנים
            if i == len(tokens) - 1 or tokens[i + 1] == token:
                terminate_phrase()
        elif token in IGNORE_WORDS and current_phrase:
            # If 'שנה' appears we include it
            current_phrase.append(raw_token)

            # Look ahead to check if another 'שנה' exists at the end of this phrase
            look_ahead_tokens = tokens[i + 1:]
            has_following_shana = any(preprocess_token(t)[0] in IGNORE_WORDS for t in look_ahead_tokens)
            if not has_following_shana:
                terminate_phrase()
        else:
            # Not a number word or ignore word while phrase_active
            terminate_phrase()

    return phrases


def get_verses_with_numbers():
    verses = []
    for verse in get_bible():
        if is_numbers_in_verse(verse.text):
            verses.append(verse)

    return verses
