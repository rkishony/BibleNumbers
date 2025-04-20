from pathlib import Path
from typing import List

from bible_types import VerseAndNumericHebrews

START = "    <!-- START -->"
END = "    <!-- END -->"

def read_template(file_name: str) -> str:
    with open(file_name, 'r') as file:
        template = file.read()

    # Remove everything between START and END:
    start_index = template.index(START) + len(START)
    end_index = template.index(END)
    template = template[:start_index] + '\n' + template[end_index:]
    return template

TEMPLATE = read_template('docs/template.html')


def create_html_of_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews],
                                       file_name='index.html'):
    all_verses = []
    for verse_and_numeric_hebrews in verses_and_numeric_hebrews:
        verse_html, location_html = verse_and_numeric_hebrews.to_html()
        all_verses.append(f"""
        <div class="row">
            <div class="locations">{location_html}</div>
            <div class="verses">{verse_html}</div>
        </div>
    """)
    html = TEMPLATE
    html = html.replace(START, START + '\n' + '\n'.join(all_verses))
    with open(Path('docs') / file_name, 'w') as file:
        file.write(html)


def create_text_of_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews],
                                       file_name='verses_with_numbers.txt'):
    with open(file_name, 'w') as file:
        for verse_and_numeric_hebrews in verses_and_numeric_hebrews:
            verse_text = verse_and_numeric_hebrews.to_text()
            file.write(f"{verse_text}\n\n")