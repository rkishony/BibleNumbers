from typing import List, Tuple

NUMBERS = {
    1: 'אחד, אחת',
    2: 'שניים, שתיים, שני, שתי',
    3: 'שלוש, שלושה, שלושת',
    4: 'ארבע, ארבעה, ארבעת',
    5: 'חמש, חמישה, חמשת',
    6: 'שש, ששהֿ, ששת',
    7: 'שבע, שיבעה, שבעת',
    8: 'שמונה, שמונת',
    9: 'תשע, תשעה, תשעת',
    10: 'עשר',
    100: 'מאה',
    1000: 'אלף',
    10000: 'רבבה',
}

NUMBERS_TO_HEBREW_NUMBERS = {number: [word.strip() for word in hebrew.split(",")] for number, hebrew in NUMBERS.items()}


def get_hatayot(hebrew_number: str, with_hatayot: bool = False):
    if with_hatayot:
        return [hebrew_number, 'ו' + hebrew_number]
    return [hebrew_number]


def iter_hebrew_numbers(with_hatayot: bool = True):
    for number, hebrew_numbers in NUMBERS_TO_HEBREW_NUMBERS.items():
        for hebrew_number in hebrew_numbers:
            yield hebrew_number
            for hataya in get_hatayot(hebrew_number, with_hatayot):
                yield hataya


def is_word_in_hebrew_numbers(word: str) -> bool:
    return word in iter_hebrew_numbers()


def is_numbers_in_verse(verse) -> bool:
    return any(is_word_in_hebrew_numbers(word) for word in verse.split(' '))
