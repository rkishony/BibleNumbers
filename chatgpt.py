# Call chatgpt

from typing import List, Optional

import openai

from openai import OpenAIError
from openai import OpenAI

from bible_types import Verse, Verses, NumericHebrew
from read_bible import clean_text
from bible_utils import search_in_bible

MODEL = "gpt-4o"

API_KEY = "YOUR KEY HERE"

SYSTEM_PROMPT = "You are a bible expert. Respond in json. Use hebrew"

EXAMPLE_VERSES = [
    search_in_bible("ארבע מאות ושבעים אלף איש שולף חרב", expected=1)[0],
    search_in_bible("ויהיו כל ימי אדם אשר חי תשע מאות שנה ושלושים שנה וימות", expected=1)[0],
]


EXAMPLE_ALL_NUMBERS = [
    NumericHebrew(book=EXAMPLE_VERSES[0].book, chapter=EXAMPLE_VERSES[0].chapter, letter=EXAMPLE_VERSES[0].letter,
                  quote="אלף אלפים ומאה אלף איש", number=1100000, entity="איש"),
    NumericHebrew(book=EXAMPLE_VERSES[0].book, chapter=EXAMPLE_VERSES[0].chapter, letter=EXAMPLE_VERSES[0].letter,
                  quote="ארבע מאות ושבעים אלף איש", number=470000, entity="איש"),
    NumericHebrew(book=EXAMPLE_VERSES[1].book, chapter=EXAMPLE_VERSES[1].chapter, letter=EXAMPLE_VERSES[1].letter,
                  quote="תשע מאות שנה, ושלושים שנה", number=930, entity="שנה"),
]


def check_match(verse: Verse, numeric_hebrew: NumericHebrew) -> Optional[bool]:
    if verse.book == numeric_hebrew.book and verse.chapter == numeric_hebrew.chapter \
            and verse.letter == numeric_hebrew.letter:
        if clean_text(numeric_hebrew.quote) in verse.text:
            return True
        else:
            return None
    return False


def get_matching_verse(verses: List[Verse], numeric_hebrew: NumericHebrew) -> Optional[Verse]:
    for verse in verses:
        if check_match(verse, numeric_hebrew):
            return verse
    return None


def get_numbers_from_verses_using_llm(verses: List[Verse]) -> List[NumericHebrew]:
    message = ''
    message += 'Here are some verses from the Bible that all cite numerical values:\n\n'
    for num, verse in enumerate(verses):
        message += str(verse) + '\n'
    message += '\n'
    message += 'Identify all the numbers in each of the verses and provide their values in JSON format, like this.\n\n'
    message += \
        '{"all_numbers": [\n' \
        '{\n' \
        '    "book": "<book name>",\n' \
        '    "chapter": "<chapter letter>",\n' \
        '    "letter": "<verse letter>",\n'  \
        '    "quote": "<extract the exact hebrew text of the number and counted entity>",\n' \
        '    "number": <the quoted number, int>,\n' \
        '    "entity": "<the counted entity>"\n' \
        '},\n' \
        'etc for all numbers you can find in above provided verses\n' \
        ']}\n\n'

    message += 'For example, if the verses were:\n\n'
    for num, verse in enumerate(EXAMPLE_VERSES):
        message += str(verse) + '\n'

    message += '\nYou would respond with:\n\n'
    message += '{"all_numbers": [\n'
    message += ',\n'.join([numeric_hebrew.to_string() for numeric_hebrew in EXAMPLE_ALL_NUMBERS])

    message += '\n]}\n\n'

    message += \
        "\nNote that each provided versus could have more than one number. "

    response = get_response(message, response_format=ListOfNumericHebrew)

    return response.all_numbers


def get_response(user_prompt, system_prompt=SYSTEM_PROMPT, api_key=API_KEY, model=MODEL, response_format=None):
    """
    Get a response from the ChatGPT-4 model.

    Parameters:
    user_prompt (str): The user prompt to send to the model.
    system_prompt (str): The system prompt to send to the model.
    api_key (str): The OpenAI API key.
    model (str): The model to use.
    is_json (bool): Whether the response should be in JSON format.

    Returns:
    dict: The response from the model.
    """
    openai.api_key = api_key

    try:
        client = OpenAI(api_key=api_key)
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format=response_format,
        )
    except OpenAIError as e:
        print(f"An error occurred: {e}")
        return None

    return response.choices[0].message.parsed


def test_chatgpt():
    response = get_numbers_from_verses_using_llm(EXAMPLE_VERSES)
    print(response)



#
#
# from pydantic import BaseModel
# from openai import OpenAI
#
# client = OpenAI()
#
# class Step(BaseModel):
#     explanation: str
#     output: str
#
# class MathReasoning(BaseModel):
#     steps: list[Step]
#     final_answer: str
#
# completion = client.beta.chat.completions.parse(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step."},
#         {"role": "user", "content": "how can I solve 8x + 7 = -23"}
#     ],
#     response_format=MathReasoning,
# )
#
# math_reasoning = completion.choices[0].message.parsed
# print(math_reasoning)


