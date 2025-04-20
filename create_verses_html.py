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
    <link rel="icon" type="image/png" sizes="64x64" href="favicon.png">
      
    <link rel="shortcut icon" href="favicon.png">
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
        .container {
          display: flex;
          flex-direction: column;
          margin: 0 20px 80px 20px; /* increase bottom from 40px → 80px */
        }
    
        /* sticky footer */
        .sticky-footer {
          position: fixed;
          bottom: 0;
          left: 0;
          width: 100%;
          background-color: #f9f9f9;
          text-align: left;
          padding: 8px 20px;
          font-size: 0.8em;
          color: #555;
          box-shadow: 0 -1px 5px rgba(0,0,0,0.1);
        }
        
        /* make location/verse columns fluid instead of fixed px */
        .locations {
          /* allocate 25% of the row (min 80px), not a rigid 150px */
          flex: 0 0 25%;
          min-width: 80px;
          max-width: 150px;
        }
        .verses {
          flex: 1 1 75%;
        }
        
        /* breakpoint for small screens (phones) */
        @media (max-width: 600px) {
          /* stack search controls vertically */
          .search-bar {
            flex-direction: column;
            align-items: stretch;
          }
          .search-bar label,
          .search-bar input,
          .search-bar button {
            width: 100%;
            margin: 5px 0;
          }
        
          /* make location column narrower on tiny screens */
          .locations {
            flex: 0 0 30%;
            min-width: 60px;
          }
        }
        .row {
          /* if you already have ‘gap’ here, just bump it up */
          gap: 12px;  
        }
        
        /* make the number‑inputs narrower on desktop */
        .search-bar input[type="number"] {
          width: 80px;  /* was 120px */
        }
        /* --- always keep min/max as a flex row, even on desktop --- */
        .range-group {
          display: flex;
          gap: 8px;
          align-items: center;
        }
        
        /* --- mobile tweaks (up to 600px wide) --- */
        @media (max-width: 600px) {
          /* everything except the range‑group still goes full width */
          .search-bar > :not(.range-group) {
            width: 100%;
            margin: 5px 0;
          }
        
        .range-group {
          display: flex;
          flex-direction: row;
          align-self: flex-start;  /* don’t stretch to full width */
          gap: 8px;
          margin: 5px 0;
          width: auto;            /* shrink to fit contents */
        }
        
        .range-group label {
          margin: 0;
          white-space: nowrap;    /* keep label next to its input */
        }
        
        .range-group input {
          flex: 0 0 60px;         /* fixed-ish width, no growing */
          margin: 0;
        }
        }

  </style>
</head>
<body>
    <a href="https://github.com/rkishony/BibleNumbers" target="_blank" rel="noopener">
      <img src="transparent_icon.png" alt="תנ״ך מ10פר" class="banner">
    </a>

    <div class="search-bar">
      <label for="searchNumber">חיפוש מספר:</label>
      <input type="number" id="searchNumber" placeholder="מספר">
      <button id="searchBtn">חפש</button>
    
      <div class="range-group">
        <label for="rangeMin">מ:</label>
        <input type="number" id="rangeMin" placeholder="מינימום">
        <label for="rangeMax">עד:</label>
        <input type="number" id="rangeMax" placeholder="מקסימום">
      </div>
      <button id="rangeBtn">טווח</button>
    
      <button id="resetBtn">הצג הכל</button>
    </div>
    <div class="container">
"""

HTML_END = """
    </div>

    <!-- this will show when no rows match -->
    <p id="noResults" style="display:none; text-align:center; margin:1em 0; font-weight:bold;">
      אין תוצאות
    </p>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
      const searchInput   = document.getElementById('searchNumber');
      const rangeMinInput = document.getElementById('rangeMin');
      const rangeMaxInput = document.getElementById('rangeMax');
    
      const searchBtn = document.getElementById('searchBtn');
      const rangeBtn  = document.getElementById('rangeBtn');
      const resetBtn  = document.getElementById('resetBtn');
    
      const rows = Array.from(document.querySelectorAll('.container .row'));
      const noResults = document.getElementById('noResults');
    
      function getNumberFromRow(row) {
        const span = row.querySelector('.verses span[style*="color:green"]');
        const m = span?.textContent.match(/\d+/);
        return m ? +m[0] : null;
      }
    
      function filterRows(pred) {
        let anyVisible = false;
        rows.forEach(r => {
          const ok = pred(getNumberFromRow(r));
          r.style.display = ok ? '' : 'none';
          if (ok) anyVisible = true;
        });
        noResults.style.display = anyVisible ? 'none' : '';
      }
    
      // specific‑number search
      searchBtn.addEventListener('click', () => {
        const v = +searchInput.value;
        if (!isNaN(v)) filterRows(n => n === v);
      });
    
      // range search
      rangeBtn.addEventListener('click', () => {
        const min = +rangeMinInput.value;
        const max = +rangeMaxInput.value;
        if (!isNaN(min) && !isNaN(max)) filterRows(n => n >= min && n <= max);
      });
    
      // reset: clear inputs & show all
      resetBtn.addEventListener('click', () => {
        searchInput.value = '';
        rangeMinInput.value = '';
        rangeMaxInput.value = '';
        rows.forEach(r => r.style.display = '');
        noResults.style.display = 'none';
      });
    
      // Enter‑key handlers
      searchInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') searchBtn.click();
      });
      [rangeMinInput, rangeMaxInput].forEach(input =>
        input.addEventListener('keydown', e => {
          if (e.key === 'Enter') rangeBtn.click();
        })
      );
    });
    </script>
      <footer class="sticky-footer">
        מוקדש באהבה לילדתי יעל קישוני
      </footer></body>
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