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
    'תשעת': 9
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

IGNORE_WORDS = {"שנה", "שנות", "שנים"}


def preprocess_token(token: str):
    """Remove leading ו and return (cleaned_token, is_conjunction)."""
    is_conjunction = False
    while token.startswith('ו') and len(token) > 1:
        token = token[1:]
        is_conjunction = True
    return token, is_conjunction


def hebrew_num_to_int(phrase: str) -> int:

    tokens = phrase.split()

    total = 0
    current_segment = 0
    segment_parts = []  # track numbers added in the current segment

    def add_number(num, is_conjunction):
        nonlocal current_segment, segment_parts
        if is_conjunction:
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
        token, is_conjunction = preprocess_token(token)

        if token in IGNORE_WORDS:
            continue

        # Units or construct forms
        if token in UNITS_AND_TENS_MAP:
            add_number(UNITS_AND_TENS_MAP[token], is_conjunction)
            continue

        # Hundreds
        if token in HUNDREDS_MAP:
            val = HUNDREDS_MAP[token]
            if is_conjunction:
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
            if is_conjunction:
                current_segment += value
                segment_parts.append(value)
            else:
                multiply_last(value)
            continue

        # token not recognized as number, we can continue or raise an error
        continue

    total += current_segment
    return total
