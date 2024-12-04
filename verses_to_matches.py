import json
import os
from typing import Dict, List, Set

from bible_types import Verse
from chatgpt import NumericHebrew

FILE_NAME = 'verses_to_numerics.json'


def dump_verses_to_numerics(file_name: str = FILE_NAME, verses_to_numerics: Dict[Verse, List[NumericHebrew]] = None):
    """to json"""
    json_obj = []
    for k, v in verses_to_numerics.items():
        json_obj.append([k._asdict()] + [x.dict() for x in v])

    with open(file_name, 'w') as file:
        json.dump(json_obj, file, ensure_ascii=False, indent=4)


def load_or_create_verses_to_numerics(file_name: str = FILE_NAME) -> Dict[Verse, List[NumericHebrew]]:
    """from pickle"""
    import pickle
    if not os.path.exists(file_name):
        return {}

    with open(file_name, 'r') as file:
        json_obj = json.load(file)
        verses_to_numerics = dict()
        for kv in json_obj:
            k = kv[0]
            v = kv[1:]
            verses_to_numerics[Verse(**k)] = [NumericHebrew(**x) for x in v]
        return verses_to_numerics
