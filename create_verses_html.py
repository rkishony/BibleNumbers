from typing import List

from bible_types import VerseAndNumericHebrews

HTML_HEAD = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hebrew Text Layout</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            direction: rtl;
        }
        .container {
            display: flex;
            flex-direction: column;
            margin: 20px;
        }
        .row {
            display: flex;
            flex-direction: row; /* Locations on the right, verses on the left */
            margin-bottom: 10px;
            align-items: flex-start; /* Align rows at the top */
        }
        .locations {
            width: 150px; /* Fixed width for the location column */
            text-align: right;
            white-space: nowrap;
            padding-right: 10px; /* Space between location and verse */
            flex-shrink: 0; /* Prevent locations from shrinking */
        }
        .verses {
            flex-grow: 1; /* Allow the verse column to shrink */
            text-align: right; /* Align text to the right */
            word-wrap: break-word; /* Allow wrapping for long text */
            overflow-wrap: break-word; /* Ensures compatibility with older browsers */
            box-sizing: border-box; /* Ensures consistent box sizing */
            display: block; /* Prevent alignment issues with inline behavior */
        }
    </style>
</head>
<body>
    <div class="container">
"""

HTML_END = """
    </div>
</body>
</html>
"""


def create_html_of_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews],
                                       file_name='verses_with_numbers.html'):
    html = HTML_HEAD
    for verse_and_numeric_hebrews in verses_and_numeric_hebrews:
        verse_html, location_html = verse_and_numeric_hebrews.to_html()
        html += f"""
        <div class="row">
            <div class="locations">{location_html}</div>
            <div class="verses">{verse_html}</div>
        </div>
    """
    html += HTML_END
    with open(file_name, 'w') as file:
        file.write(html)

