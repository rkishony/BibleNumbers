from dataclasses import dataclass
from typing import NamedTuple, List, Dict

import numpy as np
from pydantic import BaseModel


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
    number: int
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
        return hash((self.book, self.chapter, self.letter, self.quote, self.number, self.entity))


class ListOfNumericHebrew(BaseModel):
    all_numbers: List[NumericHebrew]


UNIQUE_QUOTE_COLOR = "\033[31m"  # red
REPEATED_QUOTE_COLOR = "\033[33m"  # yellow
NUMBER_COLOR = "\033[32m"  # green

RESET = "\033[0m"


@dataclass(frozen=True)
class VerseAndNumericHebrews:
    verse: Verse
    numeric_hebrews: List[NumericHebrew]

    def map_numeric_hebrews(self) -> Dict[NumericHebrew, List[int]]:
        """
        For each numeric hebrew find the index of its first appearance in the verse.
        If the match is already covered, move to the next match.
        """
        is_covered = np.zeros(len(self.verse.text), dtype=bool)
        numeric_hebrew_to_indices = {}
        numeric_hebrew_to_all_indices = {}
        for numeric_hebrew in self.numeric_hebrews:
            quote = numeric_hebrew.quote
            all_start_indices = [i for i in range(len(self.verse.text)) if self.verse.text.startswith(quote, i)]
            numeric_hebrew_to_all_indices[numeric_hebrew] = all_start_indices
            numeric_hebrew_to_indices[numeric_hebrew] = []

        while any(numeric_hebrew_to_all_indices.values()):
            for numeric_hebrew, all_start_indices in numeric_hebrew_to_all_indices.items():
                remaining_indices = all_start_indices.copy()
                for start_index in all_start_indices:
                    remaining_indices.remove(start_index)
                    if not any(is_covered[start_index:start_index + len(quote)]):
                        numeric_hebrew_to_indices[numeric_hebrew].append(start_index)
                        is_covered[start_index:start_index + len(quote)] = True
                        break
                numeric_hebrew_to_all_indices[numeric_hebrew] = remaining_indices
        return numeric_hebrew_to_indices

    def _to_colored_str(self, is_html: bool, with_non_matching: bool = True) -> str:
        text = self.verse.text
        numeric_hebrew_to_indices = self.map_numeric_hebrews()
        indices_to_numeric_hebrew_and_is_first = {index: (numeric_hebrew, k == 0)
                                                  for numeric_hebrew, indices in numeric_hebrew_to_indices.items()
                                                  for k, index in enumerate(indices)}
        # sort by index in descending order
        for start_index, (numeric_hebrew, is_first) in sorted(indices_to_numeric_hebrew_and_is_first.items(),
                                                              key=lambda x: x[0], reverse=True):
            quote = numeric_hebrew.quote
            number = numeric_hebrew.number
            entity = numeric_hebrew.entity
            if is_html:
                if is_first:
                    color = "red"
                else:
                    color = "yellow"
                highlighted_text = f"<span style='color:{color}'>{quote}</span><span style='color:green'> [{number} {entity}]</span>"
            else:
                if is_first:
                    color = UNIQUE_QUOTE_COLOR
                else:
                    color = REPEATED_QUOTE_COLOR
                highlighted_text = f"{color}{quote}{RESET}{NUMBER_COLOR} [{number} {entity}]{RESET}"
            text = text[:start_index] + highlighted_text + text[start_index + len(quote):]
        if not is_html:
            # add spaces to align the text:
            color_marks_len = len(UNIQUE_QUOTE_COLOR) + len(RESET) + len(NUMBER_COLOR) + len(RESET)
        return text

    def to_colored_text(self) -> str:
        return self._to_colored_str(is_html=False)

    def to_html(self) -> str:
        return self._to_colored_str(is_html=True)
