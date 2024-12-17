import re
from enum import Enum
from typing import Optional, Iterable, List

from bible_types import Time
from read_bible import get_bible



UNITS_MAP = {
    # Feminine
    'אַחַת': 1,
    'שְׁתַּיִם': 2,
    'שָׁלוֹשׁ': 3,
    'שָׁלֹשׁ': 3,  # Added shortened form
    'אַרְבַּע': 4,
    'חָמֵשׁ': 5,
    'חֲמֵשׁ': 5,
    'שֵׁשׁ': 6,
    'שֶׁשׁ': 6,  # Added shortened form
    'שֶׁבַע': 7,
    'שְׁמֹנֶה': 8,
    'תֵּשַׁע': 9,
    'תֵשַׁע': 9,
    'תְשַׁע': 9,  # Added shortened form
    'תְּשַׁע': 9,  # Added shortened form

    # Masculine
    'אֶחָד': 1,
    'שְׁנַיִם': 2,
    'שְׁנָיִם': 2,
    'שְׁלֹשָׁה': 3,
    'שְׁלוֹשָׁה': 3,
    'אַרְבָּעָה': 4,
    'חֲמִשָּׁה': 5,
    'שִׁשָּׁה': 6,
    'שִׁבְעָה': 7,
    'שִׁבְעָנָה': 7,
    'שְׁמוֹנָה': 8,
    'שְׁמֹנָה': 8,
    'תִּשְׁעָה': 9,

    # Construct
    'שְׁתֵּי': 2,
    'שְׁנֵי': 2,

    'שְׁלֹשֶׁת': 3,
    'אַרְבַּעַת': 4,
    'חֲמֵשֶׁת': 5,
    'שֵׁשֶׁת': 6,
    'שִׁבְעַת': 7,
    'שְׁמוֹנַת': 8,
    'תִשְׁעַת': 9,

    # Conjunctive
    'עַשְׁתֵּי': 1,
    'שְׁתֵּים': 2,
    'שְׁנֵים': 2,
    'שְּׁנֵים': 2,
    'שְׁלֹשׁ': 3,
    'אַרְבָּע': 4,
    'שְׁבַע': 7,
    'שְׁמוֹנֶה': 8,
}

TENS_NUM_MAP = {
    # Feminine
    'עֶשֶׂר': 10,
    'עָשָׂר': 10,

    'עֲשֶׂרֶת': 10,

    # Masculine
    'עֲשָׂרָה': 10,

    # Construct
    'עֶשְׂרֵה': 10,

    # Tens (neutral across genders)
    'עֶשְׂרִים': 20,
    'שְׁלוֹשִׁים': 30,
    'שְׁלֹשִׁים': 30,
    'אַרְבָּעִים': 40,
    'חֲמִשִּׁים': 50,
    'שִׁשִּׁים': 60,
    'שִׁבְעִים': 70,
    'שְׁמֹנִים': 80,
    'שְׁמוֹנִים': 80,
    'תִשְׁעִים': 90,
    'תִּשְׁעִים': 90,
}

COUPLE_MAP = {
    'מָאתַיִם': 200,
    'אַלְפַּיִם': 2000,
}

HUNDREDS_MAP = {
    'מֵאָה': 100,
    'מְאַת': 100,
}

FIXED_MAP = UNITS_MAP | TENS_NUM_MAP | COUPLE_MAP | HUNDREDS_MAP

HUNDREDS_PLURAL_MAP = {
    'מֵאוֹת': 100,
    'מֵאֹת': 100,
}

THOUSANDS_MAP = {
    'אֶלֶף': 1000,
    'אָלֶף': 1000,
}

TENTHOUSANDS_MAP = {
    'רְבָבָה': 10000,
    'רִבּוֹא': 10000
}

PLURAL_MAP = {
    'אֲלָפִים': 1000,
    'אלפים': 1000,
    'אַלְפֵי': 1000,
    'רְבָבוֹת': 10000,
    'רִבְבוֹת': 10000,
    'שָׁבֻעִים': 7,
}

ALL_PLURAL_MAP = PLURAL_MAP | TENTHOUSANDS_MAP | THOUSANDS_MAP | HUNDREDS_PLURAL_MAP

LARGER_THAN_100_MAP = THOUSANDS_MAP | TENTHOUSANDS_MAP | PLURAL_MAP

ALL_NUMBER_WORDS = set(FIXED_MAP) | set(HUNDREDS_MAP) | set(ALL_PLURAL_MAP)


SHANA_WORDS = {"שָׁנָה", "שָׁנָה", "שְׁנוֹת", "שָׁנִים", "שְׁנֵי"}
SHANA_STARTER = {"בַּשָׁנָה", "בַשָּׁנָה", "בִּשְׁנַת"}
MONTH_WORDS = {"לַחֹדֶשׁ", "לְחֹדֶשׁ", "חֹדֶשׁ", "חֳדָשִׁים", "בַחֹדֶשׁ"}
DAY_WORDS = {'יָמִים', 'יוֹם', 'הַיָּמִים'}
NIGHT_WORDS = {'לַיְלָה', 'לֵיל', 'לֵילוֹת'}
TIME_WORDS = SHANA_WORDS | MONTH_WORDS | DAY_WORDS | NIGHT_WORDS | SHANA_STARTER


EXCEPTIONS = ['האחת']

EXCEPTION_BECAUSE_OF_PREVIOUS_WORD = [
    ('בְּאֵר', 'שֶׁבַע'),
    ('בְאֵר', 'שֶׁבַע'),
    ('קִרְיַת', 'אַרְבַּע'),
    ('קִרְיַת', 'אַרְבַּע'),
    ('קִרְיַת', 'הָאַרְבַּע'),
    ('בַּת', 'שֶׁבַע'),
    ('בִּגְדֵי', 'שֵׁשׁ'),
    ('יְמֵי', 'שֵׁנִי'),
    ('תוֹלַעַת', 'שָׁנִי'),
    ('שָׁנִי', 'וְשֵׁשׁ'),
]

EXCEPTIONS_BECAUSE_OF_NEXT_WORD = [
    ('שְׁנֵי', 'חַיַּי'),
    ('שְׁנֵי', 'חַיֵּי'),
    ('שְׁנֵי', 'חַיֶּיךָ'),
    ('שְׁנֵי', 'חַיָּיו'),
    ('שְׁנֵי', 'מְגוּרַי'),
    ('שֶׁבַע', 'בֶּן'),  #  שֶׁבַע בֶּן בכרי
]

THE_ONE = [
    'אַחַת', 'אֶחָד'
]


ALL_WORDS = ALL_NUMBER_WORDS | TIME_WORDS \
            | set(w for w, _ in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD) \
            | set(w for _, w in EXCEPTIONS_BECAUSE_OF_NEXT_WORD)

class ConjugateLetter(Enum):
    """Conjugate letters with their forms for numbers and grammar."""
    BET = 'ב'
    VAV = 'ו'
    HEY = 'ה'
    MEM = 'מ'
    LAMED = 'ל'
    KAF = 'כ'


def preprocess_token(token: str, letters: Iterable[ConjugateLetter] = ConjugateLetter,
                     expected_nouns: Iterable[str] = None,
                     ) -> tuple[str, List[ConjugateLetter]]:
    """Preprocess token to identify if it's a conjunction and remove leading 'ו'."""
    if expected_nouns is not None and token in expected_nouns:
        return token, []
    nikud_pattern = "[\u0590-\u05C7]*"  # Matches Hebrew vowel signs and diacritics
    for letter in letters:
        if token.startswith(letter.value):
            pattern = f"^{letter.value}{nikud_pattern}"  # Match the conjugate letter and Nikud at the start only
            # Remove only the leading conjugate letter with Nikud
            result = re.sub(pattern, "", token)
            if expected_nouns is None:
                return result, [letter]
            if result in expected_nouns:
                return result, [letter]
            rec_token, rec_letters = preprocess_token(result, letters, expected_nouns)
            if rec_token in expected_nouns:
                return rec_token, rec_letters + [letter]
    return token, []


def tokenize(text: str) -> list[str]:
    # Define a regex pattern to match Hebrew words with vowels
    # \u0590-\u05FF covers Hebrew letters, \u05B0-\u05BC and \u05C1-\u05C2 cover Hebrew vowel signs and diacritics
    pattern = r'[\u0590-\u05FF\u05B0-\u05BC\u05C1-\u05C2]+'
    words = re.findall(pattern, text)
    return words


def hebrew_num_to_int(phrase: str) -> int:

    tokens = tokenize(phrase)

    total = 0
    current_segment = 0
    segment_parts = []  # track numbers added in the current segment

    def add_number(num, conjugate_letters):
        nonlocal current_segment, segment_parts
        if conjugate_letters == [ConjugateLetter.VAV]:
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

    def multiply_all_thus_far(factor):
        nonlocal current_segment, segment_parts, total
        # add up all parts and multiply by factor
        sum_thus_far = sum(segment_parts)
        if sum_thus_far == 0:
            if isinstance(total, Time):
                sum_thus_far = total
            else:
                sum_thus_far = max(1, total)
            total = sum_thus_far * factor
        else:
            total += sum_thus_far * factor
        segment_parts = []
        current_segment = 0

    for j, raw_token in enumerate(tokens):
        is_last = j + 1 == len(tokens)
        is_first = j == 0
        next_token = tokens[j + 1] if not is_last else None
        token, conjugate_letters = preprocess_token(raw_token, expected_nouns=ALL_WORDS)

        if token not in ALL_NUMBER_WORDS and token not in TIME_WORDS:
            print(f"Token not recognized as number: {token}")

        if is_first and token in SHANA_STARTER:
            total = Time(0, is_date=True)
            continue
        if token in SHANA_WORDS and not (token == 'שְׁנֵי' and len(segment_parts) == 0):
            multiply_all_thus_far(Time(1))
            continue
        if raw_token in ["לַחֹדֶשׁ", "לְחֹדֶשׁ", "בַחֹדֶשׁ"]:
            if not isinstance(total, Time):
                multiply_all_thus_far(Time(days=1))
            total.is_date = True
            continue
        if token in MONTH_WORDS:
            multiply_all_thus_far(Time(months=1))
            continue
        if token in DAY_WORDS:
            multiply_all_thus_far(Time(days=1))
            continue
        if token in NIGHT_WORDS:
            multiply_all_thus_far(Time(days=0))
            continue

        # Units or construct forms
        if token in FIXED_MAP:
            add_number(FIXED_MAP[token], conjugate_letters)
            continue

        # Hundreds
        if token in HUNDREDS_PLURAL_MAP:
            val = HUNDREDS_PLURAL_MAP[token]
            if conjugate_letters:
                current_segment += val
                segment_parts.append(val)
            else:
                multiply_last(val)
            continue

        if token in ALL_PLURAL_MAP:
            value = ALL_PLURAL_MAP[token]
            if conjugate_letters:
                current_segment += value
                segment_parts.append(value)
            else:
                multiply_all_thus_far(value)
            continue

        # token not recognized as number, we can continue or raise an error
        continue
    total += current_segment
    return total


def iter_hebrew_numbers(with_hatayot: bool = True):
    for unit in ALL_NUMBER_WORDS:
        yield unit


def is_word_in_hebrew_numbers(word: str) -> bool:
    return word in iter_hebrew_numbers() or preprocess_token(word)[0] in iter_hebrew_numbers()


def is_numbers_in_verse(verse) -> bool:
    return any(is_word_in_hebrew_numbers(word) for word in verse.split(' '))


def extract_number_phrases(verse: str) -> list[str]:

    raw_tokens = tokenize(verse)
    tokens_and_conjugate_letters = [preprocess_token(token, expected_nouns=ALL_WORDS
                                                     ) for token in raw_tokens]
    raw_tokens_tokens_conjugate_letters = list(zip(raw_tokens, tokens_and_conjugate_letters))
    phrases = []
    current_phrase = []

    def terminate_phrase():
        if current_phrase:
            indices_of_shana_in_current_phrase = [i for i, token in enumerate(current_phrase) if token in TIME_WORDS - SHANA_STARTER]
            last_index_of_shana = indices_of_shana_in_current_phrase[-1] if indices_of_shana_in_current_phrase else None
            if last_index_of_shana is not None and last_index_of_shana != len(current_phrase) - 1:
                phrases.append(" ".join(current_phrase[:last_index_of_shana + 1]))
                phrases.append(" ".join(current_phrase[last_index_of_shana + 1:]))
            else:
                phrases.append(" ".join(current_phrase))
            current_phrase.clear()

    prev_raw_token, prev_token = None, None
    for i, (raw_token, (token, conjugate_letters)) in enumerate(raw_tokens_tokens_conjugate_letters):
        if i + 1 < len(raw_tokens):
            next_raw_token, (next_token, next_conjugate_letters) = raw_tokens_tokens_conjugate_letters[i + 1]
        else:
            next_raw_token, next_token, next_conjugate_letters = None, None, []

        # Check if token is a number word or in the ignore words
        if conjugate_letters not in [[], [ConjugateLetter.VAV]] and current_phrase \
                and prev_token not in SHANA_STARTER:
            terminate_phrase()

        if raw_token in EXCEPTIONS:
            terminate_phrase()
        elif (prev_token, raw_token) in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD \
                or (prev_raw_token, raw_token) in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD:
            terminate_phrase()
        elif (raw_token, next_raw_token) in EXCEPTIONS_BECAUSE_OF_NEXT_WORD:
            terminate_phrase()
        elif token in THE_ONE and len(current_phrase) == 0 and next_token not in ["עֶשְׂרֵה", "לַחֹדֶשׁ"] \
                and next_conjugate_letters != [ConjugateLetter.VAV]:
            current_phrase.append(raw_token)
            terminate_phrase()
        elif token in ALL_NUMBER_WORDS or raw_token in ALL_NUMBER_WORDS:
            # if conjugate_letter in {ConjugateLetter.BET, ConjugateLetter.HEY}:
            #     terminate_phrase()
            # terminate if end of sentence, or for שנים שנים
            if prev_token == token or token == 'מֵאָה' and next_token not in TIME_WORDS and \
                    not any(preprocess_token(t, expected_nouns=ALL_WORDS)[0] in THOUSANDS_MAP | COUPLE_MAP
                            for t in current_phrase):
                terminate_phrase()

            # Start or continue a phrase
            current_phrase.append(raw_token)
        elif token in TIME_WORDS and current_phrase or token in SHANA_STARTER:
            # If 'שנה' appears we include it
            current_phrase.append(raw_token)
        else:
            # Not a number word or ignore word while phrase_active
            terminate_phrase()

        prev_raw_token, prev_token = raw_token, token

    terminate_phrase()
    return phrases


def get_verses_with_numbers():
    verses = []
    for verse in get_bible(with_nikud=True, remove_punctuations=True):
        if is_numbers_in_verse(verse.text):
            verses.append(verse)

    return verses
