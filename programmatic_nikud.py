import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, NamedTuple, Union, Optional

from bible_types import Time, NumericHebrew
from bible_utils import tokenize_words_and_punctuations
from nikud_utils import NIKUD_PATTERN
from read_bible import get_bible, get_bible_as_one_text


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
    'שְׁמֹנַת': 8,
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

ORDINAL_MAP = {
    # Masculine
    'רִאשׁוֹן': 1,
    'שֵׁנִי': 2,
    'שֵּׁנִי': 2,
    'שְׁלִישִׁי': 3,
    'רְבִיעִי': 4,
    'חֲמִישִׁי': 5,
    'שִׁשִּׁי': 6,
    'שִּׁשִּׁי': 6,
    'שְּׁבִיעִי': 7,
    'שְּׁמִינִי': 8,
    'תְּשִׁיעִי': 9,
    'עֲשִׂירִי': 10,

    # Feminine
    'רִאשׁוֹנָה': 1,
    'שְׁנִיָה': 2,
    'שֵּׁנִית': 2,
    'שְׁלִישִׁית': 3,
    'רְבִיעִית': 4,
    'חֲמִישִׁית': 5,
    'שִׁשִּׁית': 6,
    'שִּׁשִּׁית': 6,
    'שְּׁבִיעִית': 7,
    'שְּׁבִיעִת': 7,
    'שְׁמִינִית': 8,
    'תְּשִׁיעִית': 9,
    'עֲשִׂירִית': 10,
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

FIXED_MAP = UNITS_MAP | ORDINAL_MAP | TENS_NUM_MAP | COUPLE_MAP | HUNDREDS_MAP

HUNDREDS_PLURAL_MAP = {
    'מֵאוֹת': 100,
    'מֵאֹת': 100,
}

PLURAL_MAP = {
    'שָׁבֻעִים': 7,
    'עֲשָׂרֹת': 10,
    'אֶלֶף': 1000,
    'אָלֶף': 1000,
    'אֲלָפִים': 1000,
    'אלפים': 1000,
    'אַלְפֵי': 1000,
    'רְבָבוֹת': 10000,
    'רִבְבוֹת': 10000,
    'רְבָבָה': 10000,
    'רִבּוֹא': 10000
}

ALL_PLURAL_MAP = PLURAL_MAP | HUNDREDS_PLURAL_MAP

ALL_NUMBER_WORDS = set(FIXED_MAP) | set(HUNDREDS_MAP) | set(ALL_PLURAL_MAP)

# Time words
SHANA_WORDS = {"שָׁנָה", "שָׁנָה", "שְׁנוֹת", "שָׁנִים", "שְׁנֵי", "הַשָּׁנִים"}
SHANA_STARTER = {"בַשָּׁנָה", "בִּשְׁנַת", "בַּשָּׁנָה", "שְׁנַת"}
MONTH_WORDS = {"לַחֹדֶשׁ", "לְחֹדֶשׁ", "חֹדֶשׁ", "חֳדָשִׁים", "לַחֹדֶשׁ"}
MONTH_STARTER = {"בַּחֹדֶשׁ", "הַחֹדֶשׁ", "וּבַחֹדֶשׁ"}
TO_MONTH = {"לַחֹדֶשׁ", "לְחֹדֶשׁ", "בַחֹדֶשׁ"}
DAY_WORDS = {'יָמִים', 'יוֹם', 'הַיָּמִים'}
DAY_STARTER = {'בַּיּוֹם', 'יוֹם', 'וּבַיּוֹם'}
NIGHT_WORDS = {'לַיְלָה', 'לָיְלָה', 'לֵיל', 'לֵילוֹת'}
TIME_WORDS = SHANA_WORDS | MONTH_WORDS | DAY_WORDS | NIGHT_WORDS
STARTER_TIME_WORDS = SHANA_STARTER | MONTH_STARTER | DAY_STARTER
ALL_TIME_WORDS = TIME_WORDS | STARTER_TIME_WORDS

BIBLE = get_bible_as_one_text(with_nikud=True, remove_punctuations=True)
for word in ALL_NUMBER_WORDS | ALL_TIME_WORDS:
    if word not in BIBLE:
        print(f"Word not found in Bible: {word}")


EXCEPTION_BECAUSE_OF_PREVIOUS_WORD = [
    ('שָׁנִי', 'וְשֵׁשׁ'),
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

ALL_EXCEPTION_WORDS = set(w for w, _ in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD) | set(w for _, w in EXCEPTIONS_BECAUSE_OF_NEXT_WORD)

ALL_WORDS = ALL_NUMBER_WORDS | ALL_TIME_WORDS | ALL_EXCEPTION_WORDS


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

    for letter in letters:
        if token.startswith(letter.value):
            pattern = f"^{letter.value}{NIKUD_PATTERN}"  # Match the conjugate letter and Nikud at the start only
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


class ConjWord(NamedTuple):
    raw_word: str = None
    word: str = None
    conjugate_letters: List[ConjugateLetter] = None

    @classmethod
    def from_raw_word(cls, raw_word: str, expected_nouns: Iterable[str] = None):
        expected_nouns = expected_nouns or ALL_WORDS
        word, conjugate_letters = preprocess_token(raw_word, expected_nouns=expected_nouns)
        return cls(raw_word, word, conjugate_letters)


@dataclass
class GetHebrewNumbers:
    verse: str

    numeric_hebrews: List[NumericHebrew] = field(default_factory=list)
    total: Union[int, float, Time] = 0
    current_phrase_first_index: Optional[int] = None
    current_phrase_last_index: Optional[int] = None

    segment_parts: List[Union[int, float]] = field(default_factory=list)

    conj_words: List[ConjWord] = None

    @property
    def segment_sum(self):
        return sum(self.segment_parts)

    def _tokenze(self):
        is_word_and_raw_tokens = tokenize_words_and_punctuations(self.verse)
        self.conj_words = [
            ConjWord.from_raw_word(raw_token) if is_word else ConjWord(raw_token, raw_token)
            for is_word, raw_token in is_word_and_raw_tokens
        ]

    def add_number(self, num, conjugate_letters):
        if conjugate_letters == [ConjugateLetter.VAV]:
            self.segment_parts.append(num)
        else:
            if self.segment_sum == 0:
                self.segment_parts = [num]
            else:
                # Add it (rare case without 'ו'), but let's keep consistency
                self.segment_parts.append(num)

    def multiply_last(self, factor):
        if not self.segment_parts:
            # If no parts, just add factor
            self.segment_parts.append(factor)
        else:
            last = self.segment_parts.pop()
            new_val = last * factor
            self.segment_parts.append(new_val)

    def multiply_all_thus_far(self, factor):
        # add up all parts and multiply by factor
        sum_thus_far = sum(self.segment_parts)
        if sum_thus_far == 0:
            if isinstance(self.total, Time):
                sum_thus_far = self.total
            else:
                sum_thus_far = max(1, self.total)
            if isinstance(self.total, Time) and isinstance(sum_thus_far, Time):
                pass
            else:
                self.total = sum_thus_far * factor
        else:
            self.total += sum_thus_far * factor
        self.segment_parts = []

    def reset_phrase(self):
        self.total = 0
        self.current_phrase_first_index = None
        self.current_phrase_last_index = None
        self.segment_parts.clear()

    def append_phrase(self, index: int):
        if self.current_phrase_first_index is None:
            self.current_phrase_first_index = index
            is_first = True
        else:
            is_first = False
        assert self.current_phrase_last_index is None or self.current_phrase_last_index + 2 == index
        self.current_phrase_last_index = index
        raw_token, token, conjugate_letters = self.conj_words[index]

        if is_first and token in SHANA_STARTER:
            self.total = Time(0, is_date=True)
        elif is_first and token in MONTH_STARTER:
            self.total = Time(months=0, is_date=True)
        elif is_first and token in DAY_STARTER:
            self.total = Time(days=0, is_date=True)
        elif token in SHANA_WORDS and not (token == 'שְׁנֵי' and len(self.segment_parts) == 0):
            self.multiply_all_thus_far(Time(1))
        elif raw_token in TO_MONTH:
            if not isinstance(self.total, Time):
                self.multiply_all_thus_far(Time(days=1))
            self.total.is_date = True
        elif token in MONTH_WORDS:
            self.multiply_all_thus_far(Time(months=1))
        elif token in DAY_WORDS:
            self.multiply_all_thus_far(Time(days=1))
        elif token in NIGHT_WORDS:
            self.multiply_all_thus_far(Time(days=0))
        elif token in FIXED_MAP:
            self.add_number(FIXED_MAP[token], conjugate_letters)
        elif token in ALL_PLURAL_MAP:
            value = ALL_PLURAL_MAP[token]
            if conjugate_letters:
                self.segment_parts.append(value)
            else:
                if token in HUNDREDS_PLURAL_MAP:
                    self.multiply_last(value)
                else:
                    self.multiply_all_thus_far(value)

    def terminate_phrase(self):
        if self.current_phrase_first_index is None:
            return
        self.total += self.segment_sum
        if isinstance(self.total, Time) and self.total.to_number() > 0 or not isinstance(self.total, Time) and self.total > 0:
            self.numeric_hebrews.append(NumericHebrew(
                book='',
                chapter='',
                letter='',
                quote=''.join(conj_word.raw_word
                               for conj_word in self.conj_words[self.current_phrase_first_index:self.current_phrase_last_index + 1]),
                number=self.total,
                entity='',
            ))
        self.reset_phrase()

    def get(self):
        self._tokenze()
        conj_words = self.conj_words
        for j in range(0, len(conj_words), 2):
            current_word = conj_words[j]
            previous_word = conj_words[j-2] if j-2 >= 0 else ConjWord()
            next_word = conj_words[j+2] if j+2 < len(conj_words) else ConjWord()

            # Should we terminate the current phrase before adding the current word?
            if current_word.conjugate_letters not in [[], [ConjugateLetter.VAV]] \
                    and previous_word.word not in STARTER_TIME_WORDS and current_word.raw_word not in TO_MONTH:
                self.terminate_phrase()
            elif current_word.word in STARTER_TIME_WORDS and current_word.word not in TIME_WORDS:
                self.terminate_phrase()
            elif previous_word.raw_word == current_word.raw_word:
                self.terminate_phrase()
            elif current_word.raw_word == 'מֵאָה' and next_word.word not in ALL_TIME_WORDS \
                and self.current_phrase_first_index is not None \
                    and not any(
                conj_words[t].word in ALL_PLURAL_MAP | COUPLE_MAP for t in range(self.current_phrase_first_index, j)):
                self.terminate_phrase()

            if (previous_word.word, current_word.raw_word) in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD \
                    or (previous_word.raw_word, current_word.raw_word) in EXCEPTION_BECAUSE_OF_PREVIOUS_WORD:
                self.terminate_phrase()
            elif (current_word.word, next_word.raw_word) in EXCEPTIONS_BECAUSE_OF_NEXT_WORD:
                self.terminate_phrase()
            elif current_word.word in THE_ONE and self.current_phrase_first_index is None \
                    and next_word.raw_word not in ["עֶשְׂרֵה", "לַחֹדֶשׁ"] \
                    and next_word.conjugate_letters != [ConjugateLetter.VAV]:
                self.append_phrase(j)
                self.terminate_phrase()
            elif current_word.word in ALL_NUMBER_WORDS:
                self.append_phrase(j)
            elif current_word.word in ALL_TIME_WORDS and self.current_phrase_first_index is not None or current_word.word in STARTER_TIME_WORDS:
                self.append_phrase(j)
            else:
                self.terminate_phrase()
        self.terminate_phrase()
        return self.numeric_hebrews


def iter_hebrew_numbers(with_hatayot: bool = True):
    for unit in ALL_NUMBER_WORDS:
        yield unit


def is_word_in_hebrew_numbers(word: str) -> bool:
    return word in iter_hebrew_numbers() or preprocess_token(word, expected_nouns=ALL_WORDS)[0] in iter_hebrew_numbers()


def is_numbers_in_verse(verse) -> bool:
    is_word_and_token = tokenize_words_and_punctuations(verse)
    words = [word for is_word, word in is_word_and_token if is_word]
    return any(is_word_in_hebrew_numbers(word) for word in words)


def get_verses_with_numbers(with_nikud: bool = True, remove_punctuations: bool = True) -> list:
    verses = []
    for verse in get_bible(with_nikud=with_nikud, remove_punctuations=remove_punctuations):
        if is_numbers_in_verse(verse.text):
            verses.append(verse)

    return verses
