from pathlib import Path
from typing import List

from bible_types import VerseAndNumericHebrews

HTML_HEAD = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תנ״ך מ10פר</title>
    <style>
        body {
            font-family: "Arial", sans-serif;
            margin: 0;
            padding: 0;
            direction: rtl;
            background-color: #f9f9f9;
            color: #222;
        }

        .banner {
            width: 100%;
            max-height: 150px;
            object-fit: contain;
            display: block;
            margin: 10px auto;
        }

        .search-bar {
            background-color: #fff;
            padding: 20px;
            margin: 0 20px 20px 20px;
            border-radius: 12px;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            justify-content: flex-start;
        }

        .search-bar input[type="number"] {
            padding: 8px 12px;
            font-size: 1em;
            border: 1px solid #ccc;
            border-radius: 8px;
            width: 120px;
        }

        .search-bar button {
            padding: 8px 16px;
            font-size: 1em;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }

        .search-bar button:hover {
            background-color: #45a049;
        }

        .container {
            display: flex;
            flex-direction: column;
            margin: 0 20px 40px 20px;
        }

        .row {
            display: flex;
            flex-direction: row;
            margin-bottom: 10px;
            align-items: flex-start;
            background-color: #fff;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 0 5px rgba(0,0,0,0.05);
        }

        .locations {
            width: 150px;
            text-align: right;
            white-space: nowrap;
            padding-right: 10px;
            font-weight: bold;
            flex-shrink: 0;
        }

        .verses {
            flex-grow: 1;
            text-align: right;
            word-wrap: break-word;
            overflow-wrap: break-word;
            box-sizing: border-box;
        }
    </style>
</head>
<body>
    <img src="transparent_icon.png" alt="תנ״ך מ10פר" class="banner">

    <div class="search-bar">
        <label for="searchNumber">חיפוש מספר:</label>
        <input type="number" id="searchNumber" placeholder="לדוגמה: 40">
        <button>חפש</button>

        <label for="rangeMin">מ:</label>
        <input type="number" id="rangeMin" placeholder="מינימום">

        <label for="rangeMax">עד:</label>
        <input type="number" id="rangeMax" placeholder="מקסימום">
        <button>טווח</button>
    </div>

    <div class="container">
"""

HTML_END = """
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', () => {
      // grab inputs
      const searchInput   = document.getElementById('searchNumber');
      const rangeMinInput = document.getElementById('rangeMin');
      const rangeMaxInput = document.getElementById('rangeMax');
      // grab buttons by their order in the .search-bar
      const [searchBtn, rangeBtn] = document.querySelectorAll('.search-bar button');
      // all your rows
      const rows = Array.from(document.querySelectorAll('.container .row'));

      // helper: extract the first integer found in the green span of a row
      function getNumberFromRow(row) {
        const span = row.querySelector('.verses span[style*="color:green"]');
        if (!span) return null;
        const m = span.textContent.match(/\d+/);
        return m ? parseInt(m[0], 10) : null;
      }

      // show only rows where predicate(num) is true
      function filterRows(predicate) {
        rows.forEach(row => {
          const num = getNumberFromRow(row);
          row.style.display = (num !== null && predicate(num)) ? '' : 'none';
        });
      }

      // specific-number search
      searchBtn.addEventListener('click', () => {
        const v = parseInt(searchInput.value, 10);
        if (isNaN(v)) return;
        filterRows(n => n === v);
      });

      // range search
      rangeBtn.addEventListener('click', () => {
        const min = parseInt(rangeMinInput.value, 10);
        const max = parseInt(rangeMaxInput.value, 10);
        if (isNaN(min) || isNaN(max)) return;
        filterRows(n => n >= min && n <= max);
      });
    });
    </script>
</body>
</html>
"""


def create_html_of_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews],
                                       file_name='index.html'):
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
    with open(Path('docs') / file_name, 'w') as file:
        file.write(html)


def create_text_of_verses_with_numbers(verses_and_numeric_hebrews: List[VerseAndNumericHebrews],
                                       file_name='verses_with_numbers.txt'):
    with open(file_name, 'w') as file:
        for verse_and_numeric_hebrews in verses_and_numeric_hebrews:
            verse_text = verse_and_numeric_hebrews.to_text()
            file.write(f"{verse_text}\n\n")