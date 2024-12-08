from enum import Enum
from typing import Optional, Iterable

from read_bible import get_bible

UNITS_MAP = {
    # Feminine
    'אַחַת': 1,
    'שְׁתַּיִם': 2,
    'שָׁלוֹשׁ': 3,
    'אַרְבַּע': 4,
    'חָמֵשׁ': 5,
    'שֵׁשׁ': 6,
    'שֶׁבַע': 7,
    'שְׁמוֹנֶה': 8,
    'תֵּשַׁע': 9,

    # Masculine
    'אֶחָד': 1,
    'שְׁנַיִם': 2,
    'שְׁלוֹשָׁה': 3,
    'אַרְבָּעָה': 4,
    'חֲמִשָּׁה': 5,
    'שִׁשָּׁה': 6,
    'שִׁבְעָה': 7,
    'שְׁמוֹנָה': 8,
    'תִּשְׁעָה': 9,

    # Construct
    'שְׁתֵּי': 2,
    'שְׁנֵי': 2,
    'שְׁלוֹשֶׁת': 3,
    'אַרְבַּעַת': 4,
    'חֲמֵשֶׁת': 5,
    'שֵׁשֶׁת': 6,
    'שִׁבְעַת': 7,
    'שְׁמוֹנַת': 8,
    'תִּשְׁעַת': 9,

    # Conjunctive
    'שְׁתֵּים': 2,
    'שְׁנֵים': 2,
}

TENS_MAP = {
    # Feminine
    'עֶשֶׂר': 10,

    # Masculine
    'עֲשָׂרָה': 10,

    # Tens (neutral across genders)
    'עֶשְׂרִים': 20,
    'שְׁלוֹשִׁים': 30,
    'אַרְבָּעִים': 40,
    'חֲמִשִּׁים': 50,
    'שִׁשִּׁים': 60,
    'שִׁבְעִים': 70,
    'שְׁמוֹנִים': 80,
    'תִּשְׁעִים': 90,
}

UNITS_AND_TENS_MAP = UNITS_MAP | TENS_MAP

HUNDREDS_MAP = {
    'מֵאָה': 100, 'מְאַת': 100,
    'מָאתַיִם': 200
}

THOUSANDS_MAP = {
    'אֶלֶף': 1000,
    'אַלְפַּיִם': 2000
}

TENTHOUSANDS_MAP = {
    'רְבָבָה': 10000,
    'רִבּוֹא': 10000
}

PLURAL_MAP = {
    'מֵאוֹת': 100,
    'אֲלָפִים': 1000,
    'רְבָבוֹת': 10000
}

ALL_PLURAL_MAP = PLURAL_MAP | TENTHOUSANDS_MAP | THOUSANDS_MAP


ALL_NUMBER_WORDS = set(UNITS_AND_TENS_MAP) | set(HUNDREDS_MAP) | set(ALL_PLURAL_MAP)


SHANA_WORDS = {"שָׁנָה", "שָׁנוֹת", "חוֹדֶשׁ", "חוֹדְשִׁים", "שָׁנִים"}


class ConjugateLetter(Enum):
    """Conjugate letters with their forms for numbers and grammar."""

    # BET Forms
    BET_SHEVA = 'בְּ'  # Default form: "in"
    BET_CHIRIK = 'בִּ'  # Before definite nouns: "in the"
    BET_PATACH = 'בַּ'  # Rare but used in specific cases (e.g., poetic forms)

    # VAV Forms
    VAV_SHEVA = 'וְ'  # Default form: "and"
    VAV_SHURUK = 'וּ'  # Before labials (ב, מ, פ) or rounded vowels
    VAV_CHIRIK = 'וִ'  # Before chirik-based vowels (e.g., "and Israel")
    VAV_KAMATZ = 'וָ'  # Used in emphatic or poetic contexts

    # HEY Forms
    HEY_PATACH = 'הַ'  # Default form: "the"
    HEY_KAMATZ = 'הָ'  # Before guttural letters (ע, א, ח, ה)
    HEY_SEGOL = 'הֶ'  # Occasional usage, such as in "הֶחָכָם"

    # MEM Forms
    MEM_CHIRIK = 'מִ'  # Default form: "from"
    MEM_SEGOL = 'מֶ'  # Before guttural letters (e.g., "from the city")
    MEM_SHURUK = 'מוּ'  # Poetic or archaic usage

    # LAMED Forms
    LAMED_SHEVA = 'לְ'  # Default form: "to"
    LAMED_CHIRIK = 'לִ'  # Before definite nouns: "to the"
    LAMED_PATACH = 'לַ'  # Before composite sheva or specific contexts

    # KAF Forms
    KAF_SHEVA = 'כְּ'  # Default form: "like/as"
    KAF_CHIRIK = 'כִּ'  # Before definite nouns: "like the"
    KAF_PATACH = 'כַּ'  # Rare, poetic usage


def preprocess_token(token: str, letters: Iterable[ConjugateLetter] = ConjugateLetter) -> tuple[str, Optional[ConjugateLetter]]:
    """Preprocess token to identify if it's a conjunction and remove leading 'ו'."""
    for letter in letters:
        if token.startswith(letter.value):
            return token[len(letter.value):], letter
    return token, None


def tokenize(phrase: str) -> list[str]:
    return phrase.split()


def hebrew_num_to_int(phrase: str) -> int:

    tokens = tokenize(phrase)

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

    for j, token in enumerate(tokens):
        is_last = j + 1 == len(tokens)
        is_first = j == 0
        next_token = tokens[j + 1] if not is_last else None
        if token in ALL_NUMBER_WORDS:
            conjugate_letter = None
        else:
            if total:
                token, conjugate_letter = preprocess_token(token,
                                                           [ConjugateLetter.VAV_SHEVA, ConjugateLetter.VAV_SHURUK])
            else:
                token, conjugate_letter = preprocess_token(token)

        if token in SHANA_WORDS:
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
        if with_hatayot:
            yield ConjugateLetter.VAV_SHEVA.value + unit
            yield ConjugateLetter.VAV_SHURUK.value + unit


def is_word_in_hebrew_numbers(word: str) -> bool:
    return word in iter_hebrew_numbers()


def is_numbers_in_verse(verse) -> bool:
    return any(is_word_in_hebrew_numbers(word) for word in verse.split(' '))


EXCEPTIONS = ['האחת']

EXCEPTION_BECAUSE_OF_PREVIOUS_WORD = [
    ('בְּאֵר', 'שֶׁבַע'),
    ('קִרְיַת', 'אַרְבַּע'),
    ('בִּגְדֵי', 'שֵׁשׁ'),
    ('יְמֵי', 'שֵׁנִי'),
    ('תוֹלַעַת', 'שָׁנִי'),
    ('שָׁנִי', 'וְשֵׁשׁ'),
]

EXCEPTIONS_BECAUSE_OF_NEXT_WORD = [
    ('שְׁנֵי', 'חַיֵי'),
    ('שְׁנֵי', 'חַיֶּיךָ'),
    ('שְׁנֵי', 'חַיָּיו'),
]

UNALLOWED_PHRASES = [
]


def extract_number_phrases(verse: str) -> list[str]:

    tokens = tokenize(verse)
    phrases = []
    current_phrase = []

    def terminate_phrase():
        if current_phrase:
            joined_current_phrase = " ".join(current_phrase)
            if joined_current_phrase not in UNALLOWED_PHRASES:
                phrases.append(joined_current_phrase)
            current_phrase.clear()

    prev_raw_token, prev_token = None, None
    for i, raw_token in enumerate(tokens):
        # Preprocess token to identify if it's conjunction and remove leading 'ו'
        if raw_token in ALL_NUMBER_WORDS:
            conjugate_letter = None
            token = raw_token
        else:
            token, conjugate_letter = preprocess_token(raw_token)

        next_token = tokens[i + 1] if i + 1 < len(tokens) else None
        # Check if token is a number word or in the ignore words
        if raw_token in EXCEPTIONS:
            terminate_phrase()
        elif (prev_token, raw_token) in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD \
                or (prev_raw_token, raw_token) in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD:
            terminate_phrase()
        elif (raw_token, next_token) in EXCEPTIONS_BECAUSE_OF_NEXT_WORD:
            terminate_phrase()
        elif token in ALL_NUMBER_WORDS or raw_token in ALL_NUMBER_WORDS:
            # if conjugate_letter in {ConjugateLetter.BET, ConjugateLetter.HEY}:
            #     terminate_phrase()
            # terminate if end of sentence, or for שנים שנים
            if prev_raw_token == raw_token:
                terminate_phrase()
            # Start or continue a phrase
            current_phrase.append(raw_token)
        elif token in SHANA_WORDS and current_phrase:
            # If 'שנה' appears we include it
            current_phrase.append(raw_token)

            # Look ahead to check if another 'שנה' exists at the end of this phrase
            look_ahead_tokens = tokens[i + 1:]
            has_following_shana = any(preprocess_token(t)[0] in SHANA_WORDS for t in look_ahead_tokens)
            if not has_following_shana:
                terminate_phrase()
        else:
            # Not a number word or ignore word while phrase_active
            terminate_phrase()

        prev_raw_token, prev_token = raw_token, token

    terminate_phrase()
    return phrases


def get_verses_with_numbers():
    verses = []
    for verse in get_bible(with_nikud=True):
        if is_numbers_in_verse(verse.text):
            verses.append(verse)

    return verses
