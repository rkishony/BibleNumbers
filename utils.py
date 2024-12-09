import re


def search_nikud_text_for_non_nikud_query(text: str, query: str):
    """
    Search for all occurrences of a non-voweled query in a voweled Hebrew text
    and return their start and end indices in the original text.

    :param text: The original Hebrew text with vowels (nikud).
    :param query: The search query without vowels.
    :return: A list of (start_index, end_index) pairs for each match,
             or an empty list if no match.
    """
    nikud_pattern = re.compile(r'[\u05B0-\u05C7]')

    def remove_nikud(txt):
        return re.sub(nikud_pattern, '', txt)

    # Build a clean version of the text and index mapping
    mapping = []
    clean_text = []
    for i, ch in enumerate(text):
        if not re.match(nikud_pattern, ch):
            clean_text.append(ch)
            mapping.append(i)

    clean_text = ''.join(clean_text)
    clean_query = remove_nikud(query)

    # Find all occurrences of the cleaned query in the cleaned text
    start = 0
    match_positions = []
    while True:
        pos = clean_text.find(clean_query, start)
        if pos == -1:
            break
        start_index = mapping[pos]
        # Determine the end index (inclusive) in the original text
        last_letter_index = mapping[pos + len(clean_query) - 1]
        # Extend the end index to include all subsequent nikud
        end_index = last_letter_index
        while end_index + 1 < len(text) and re.match(nikud_pattern, text[end_index + 1]):
            end_index += 1
        match_positions.append((start_index, end_index))
        start = pos + 1  # Move start forward to find overlapping matches if needed

    return match_positions


def find_all_unique_nikud_of_non_nikud_query(text: str, query: str):
    """
    Find all unique occurrences of a non-voweled query in a voweled Hebrew text,
    and return the start and end indices of the query in the original text.

    :param text: The original Hebrew text with vowels (nikud).
    :param query: The search query without vowels.
    :return: A list of (start_index, end_index) pairs for each unique match,
             or an empty list if no match.
    """
    matches = search_nikud_text_for_non_nikud_query(text, query)
    unique_matches = set()
    for start, end in matches:
        unique_matches.add(text[start:end + 1])
    return unique_matches


def find_all_start_indices(text, query):
    start = 0
    while True:
        start = text.find(query, start)
        if start == -1:
            return
        yield start
        start += 1


def remove_vowels(text: str) -> str:
    return re.sub(r'[\u05B0-\u05C7]', '', text)
