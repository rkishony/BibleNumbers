from bible_utils import tokenize_words_and_punctuations, reconstruct
from utils import search_nikud_text_for_non_nikud_query


def test_search_nikud_text_for_non_nikud_query():
    text = "בְּרָכָהְ בְּרָכָה תּוֹדָה"
    query = "ברכה"
    result = search_nikud_text_for_non_nikud_query(text, query)
    assert result == [(0, 8), (10, 17)]


def test_tokenize():
    s = "הוּא וַאֲנָשִׁים--מִיהוּדָה"
    tokens = tokenize_words_and_punctuations(s)
    reconstructed = reconstruct(tokens)

    # Separate into words and separators for display
    words = [part for t, part in tokens if t]
    separators = [part for t, part in tokens if not t]

    assert reconstructed == s
    assert words == ["הוּא", "וַאֲנָשִׁים", "מִיהוּדָה"]
    assert separators == [" ", "--"]
