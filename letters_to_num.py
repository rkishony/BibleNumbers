LETTERS_TO_NUM = {
    'א': 1,
    'ב': 2,
    'ג': 3,
    'ד': 4,
    'ה': 5,
    'ו': 6,
    'ז': 7,
    'ח': 8,
    'ט': 9,
    'י': 10,
    'כ': 20,
    'ל': 30,
    'מ': 40,
    'נ': 50,
    'ס': 60,
    'ע': 70,
    'פ': 80,
    'צ': 90,
    'ק': 100,
    'ר': 200,
    'ש': 300,
    'ת': 400
}


def convert_hebrew_letter_to_num(hebrew: str):
    """
    Convert a Hebrew letter to its corresponding number.
    """
    return LETTERS_TO_NUM.get(hebrew, None)


def convert_hebrew_string_to_num(hebrew: str):
    """
    Convert a Hebrew string to its corresponding number.
    """
    total = 0
    for letter in hebrew:
        num = convert_hebrew_letter_to_num(letter)
        if num is not None:
            total += num
        else:
            raise ValueError(f"Invalid Hebrew letter: {letter}")
    return total
