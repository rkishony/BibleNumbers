from chatgpt import get_numbers_from_verses_using_llm, get_matching_verse
from numbers_in_words import NUMBERS, is_numbers_in_verse
from read_bible import BIBLE
from verses_to_matches import load_or_create_verses_to_numerics, dump_verses_to_numerics


def get_verses_with_numbers():
    verses = []
    for verse in BIBLE:
        if is_numbers_in_verse(verse):
            verses.append(verse)
            break

    return verses


BATCH_SIZE = 10


def main():
    verses = get_verses_with_numbers()
    print('Found', len(verses), 'verses with numbers')
    verses_to_numerics = load_or_create_verses_to_numerics()
    batch = []
    for index, verse in enumerate(verses):
        if verse in verses_to_numerics and verses_to_numerics[verse]:
            print('Skipping verse:', verse)
            continue
        batch.append(verse)
        if len(batch) < BATCH_SIZE:
            continue

        numeric_hebrews = get_numbers_from_verses_using_llm(batch)
        matching_verses = set()
        for numeric_hebrew in numeric_hebrews:
            matching_verse = get_matching_verse(batch, numeric_hebrew)
            if matching_verse is not None:
                verses_to_numerics[matching_verse] = verses_to_numerics.get(matching_verse, []) + [numeric_hebrew]
                matching_verses.add(matching_verse)
            else:
                print('No matching verse for numeric:', numeric_hebrew)
        for verse in batch:
            if verse not in matching_verses:
                verses_to_numerics[verse] = []
            print('Verse:', verse)
            if not verses_to_numerics[verse]:
                print('   No numeric found')
            for numeric_hebrew in verses_to_numerics[verse]:
                print('   ', numeric_hebrew)
        print('-----------------------------------', index)
        batch = []
        dump_verses_to_numerics(verses_to_numerics=verses_to_numerics)


if __name__ == "__main__":
    main()
