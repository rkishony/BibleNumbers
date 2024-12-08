from utils import search_nikud_text_for_non_nikud_query


def test_search_nikud_text_for_non_nikud_query():
    text = "בְּרָכָהְ בְּרָכָה תּוֹדָה"
    query = "ברכה"
    result = search_nikud_text_for_non_nikud_query(text, query)
    assert result == [(0, 8), (10, 17)]
