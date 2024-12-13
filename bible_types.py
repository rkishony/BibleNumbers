from dataclasses import dataclass
from typing import NamedTuple, List, Dict, Union, Tuple

import numpy as np
from pydantic import BaseModel

from utils import find_all_start_indices


class Verse(NamedTuple):
    book: str
    chapter: str
    letter: str
    text: str

    def __str__(self):
        return f'Verse(book="{self.book}", chapter="{self.chapter}", letter="{self.letter}", text="{self.text.strip()}")'


Verses = List[Verse]


class NumericHebrew(BaseModel):
    book: str
    chapter: str
    letter: str
    quote: str
    number: Union[int, float]
    entity: str

    def to_string(self):
        return \
            '{\n' \
            '   "book": "' + self.book + '",\n' \
            '   "chapter": "' + self.chapter + '",\n' \
            '   "letter": "' + self.letter + '",\n' \
            '   "quote": "' + self.quote + '",\n' \
            '   "number": ' + str(self.number) + ',\n' \
            '   "entity": "' + self.entity + '"\n' \
            '}'

    def __hash__(self):
        return id(self)


class ListOfNumericHebrew(BaseModel):
    all_numbers: List[NumericHebrew]


UNIQUE_QUOTE_COLOR = "\033[31m"  # red
REPEATED_QUOTE_COLOR = "\033[33m"  # yellow
NUMBER_KEYWORD_COLOR = "\033[34m"  # blue
NUMBER_COLOR = "\033[32m"  # green

RESET = "\033[0m"
WIDTH = 180


@dataclass(frozen=True)
class VerseAndNumericHebrews:
    verse: Verse
    numeric_hebrews: List[NumericHebrew]

    def map_numeric_hebrews(self, show_only_one_match: bool = True) -> Dict[Union[NumericHebrew, str], List[int]]:
        """
        For each numeric hebrew find the index of its first appearance in the verse.
        If the match is already covered, move to the next match.
        """
        from programmatic import iter_hebrew_numbers

        is_covered = np.zeros(len(self.verse.text), dtype=bool)
        numeric_hebrew_to_indices = {}
        numeric_hebrew_to_all_indices = {}
        for numeric_hebrew in self.numeric_hebrews:
            all_start_indices = list(find_all_start_indices(self.verse.text, numeric_hebrew.quote))
            numeric_hebrew_to_all_indices[numeric_hebrew] = all_start_indices
            numeric_hebrew_to_indices[numeric_hebrew] = []

        while any(numeric_hebrew_to_all_indices.values()):
            for numeric_hebrew, all_start_indices in numeric_hebrew_to_all_indices.items():
                remaining_indices = all_start_indices.copy()
                for start_index in all_start_indices:
                    remaining_indices.remove(start_index)
                    len_quote = len(numeric_hebrew.quote)
                    if not any(is_covered[start_index:start_index + len_quote]):
                        numeric_hebrew_to_indices[numeric_hebrew].append(start_index)
                        is_covered[start_index:start_index + len_quote] = True
                        break
                numeric_hebrew_to_all_indices[numeric_hebrew] = remaining_indices
            if show_only_one_match:
                break
        for numeric_keyword in iter_hebrew_numbers():
            all_start_indices = list(find_all_start_indices(' ' + self.verse.text + ' ', ' ' + numeric_keyword + ' '))
            available_indices = []
            for start_index in all_start_indices:
                if not any(is_covered[start_index:start_index + len(numeric_keyword)]):
                    available_indices.append(start_index)
                    is_covered[start_index:start_index + len(numeric_keyword)] = True
            if available_indices:
                numeric_hebrew_to_indices[numeric_keyword] = available_indices
        return numeric_hebrew_to_indices

    def _to_colored_str(self, is_html: bool) -> str:
        text = self.verse.text
        numeric_hebrew_to_indices = self.map_numeric_hebrews()
        indices_to_numeric_hebrew_and_is_first = {index: (numeric_hebrew, k == 0)
                                                  for numeric_hebrew, indices in numeric_hebrew_to_indices.items()
                                                  for k, index in enumerate(indices)}
        text_len = len(text)
        for start_index, (numeric_hebrew, is_first) in sorted(indices_to_numeric_hebrew_and_is_first.items(),
                                                              key=lambda x: x[0], reverse=True):
            is_keyword = isinstance(numeric_hebrew, str)
            if is_keyword:
                quote = numeric_hebrew
                bracket = ""
            else:
                quote = numeric_hebrew.quote
                if numeric_hebrew.entity:
                    bracket = f" [{numeric_hebrew.number} {numeric_hebrew.entity}]"
                else:
                    bracket = f" [{numeric_hebrew.number}]"
            assert quote == text[start_index:start_index + len(quote)]
            if is_html:
                if not is_keyword:
                    color = "blue" if is_first else "cyan"
                else:
                    color = "orange"
                highlighted_text = f"<span style='color:{color}'>{quote}</span>"
                if bracket:
                    bracket_color = "green"
                    highlighted_text += f"<span style='color:{bracket_color}'>{bracket}</span>"
            else:
                if not is_keyword:
                    color = UNIQUE_QUOTE_COLOR if is_first else REPEATED_QUOTE_COLOR
                else:
                    color = NUMBER_KEYWORD_COLOR
                highlighted_text = f"{color}{quote}{RESET}"
                if bracket:
                    highlighted_text += f"{NUMBER_COLOR}{bracket}{RESET}"
            text_len += len(bracket)
            text = text[:start_index] + highlighted_text + text[start_index + len(quote):]
        if not is_html:
            text = " " * (WIDTH - text_len) + text
        return text

    def to_colored_text(self) -> str:
        return self._to_colored_str(is_html=False)

    def to_html(self) -> Tuple[str, str]:
        verse_html = self._to_colored_str(is_html=True)
        location_html = f"{self.verse.book} {self.verse.chapter} {self.verse.letter}"

        return verse_html, location_html
