def hebrew_num_to_int(phrase: str) -> int:
    units_map = {
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

    tens_map = {
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

    hundreds_map = {
        'מאה': 100, 'מאת': 100,
        'מאתיים': 200
    }

    thousands_map = {
        'אלף': 1000,
        'אלפיים': 2000
    }

    # Ten-thousands:
    # "רבבה" = 10,000
    # "ריבוא" = 10,000
    # "רבבות" = number * 10,000 if preceded by a number, else 10,000
    tenthousands_map = {
        'רבבה': 10000,
        'ריבוא': 10000
    }

    ignore_words = {"שנה", "שנות", "שנים"}

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
        # Check for leading 'ו'
        is_conjunction = False
        while token.startswith('ו') and len(token) > 1:
            token = token[1:]
            is_conjunction = True

        if token in ignore_words:
            continue

        # Units or construct forms
        if token in units_map:
            add_number(units_map[token], is_conjunction)
            continue

        # Tens
        if token in tens_map:
            add_number(tens_map[token], is_conjunction)
            continue

        # Hundreds
        if token in hundreds_map:
            val = hundreds_map[token]
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

        if token == 'מאות':
            # Plural hundreds
            if is_conjunction:
                current_segment += 100
                segment_parts.append(100)
            else:
                multiply_last(100)
            continue

        # Thousands
        if token in thousands_map:
            val = thousands_map[token]
            if is_conjunction:
                # Add 1000 or 2000
                current_segment += val
                segment_parts.append(val)
            else:
                multiply_last(val)
            continue

        if token == 'אלפים':
            # Like plural thousands
            if is_conjunction:
                current_segment += 1000
                segment_parts.append(1000)
            else:
                multiply_last(1000)
            continue

        # Ten-thousands
        if token in tenthousands_map:
            # רבבה or ריבוא = 10,000
            val = tenthousands_map[token]
            if is_conjunction:
                # Add 10,000
                current_segment += val
                segment_parts.append(val)
            else:
                multiply_last(val)
            continue

        if token == 'רבבות':
            # Plural of ten-thousands (x * 10,000)
            if is_conjunction:
                current_segment += 10000
                segment_parts.append(10000)
            else:
                multiply_last(10000)
            continue

        # If we reach here, token not recognized as number
        # Ignore or you can raise an error if needed
        # For now, just ignore
        continue

    total += current_segment
    return total
