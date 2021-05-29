import contextlib

from anki.importing import AnkiPackageImporter

import orglearn.utils as utils
from orglearn.anki.anki_convertor import AnkiConvertor


@contextlib.contextmanager
def open_apkg(apkg_path):
    with utils.create_empty_anki_collection() as col:
        imp = AnkiPackageImporter(col, str(apkg_path))
        imp.run()

        yield col


def notes_iterator(col):
    for card_id in col.find_cards(""):
        yield col.getCard(card_id).note()


def test_basic(tmp_path, data_folder):
    # Initalize convertor
    c = AnkiConvertor()

    # Convert
    org_file = data_folder / "anki.org"
    out_file = tmp_path / "anki.apkg"
    c.convert(str(org_file), str(out_file))

    # Open the anki deck
    with open_apkg(str(out_file)) as col:

        notes = list(notes_iterator(col))

        expected_cards = [
            ("First node", "First body"),
            ("First node -> First First node", "First First body"),
            ("First node -> First Second node", ""),
            ("Second node", "Second body"),
            ("Second node -> Second First node", "<br />" * 4),
            ("Third node", "Third body"),
            ("Third node -> Third First node", "Third First body"),
        ]

        assert len(expected_cards) == len(notes)

        for (title, body) in expected_cards:
            assert any(title == note.fields[0] and body == note.fields[1] for note in notes)


def test_exclude_empty(tmp_path, data_folder):
    # Initalize convertor
    c = AnkiConvertor(exclude_empty=True)

    # Convert
    org_file = data_folder / "anki.org"
    out_file = tmp_path / "anki.apkg"
    c.convert(str(org_file), str(out_file))

    # Open the anki deck
    with open_apkg(str(out_file)) as col:

        notes = list(notes_iterator(col))

        expected_cards = [
            ("First node", "First body"),
            ("First node -> First First node", "First First body"),
            ("Second node", "Second body"),
            ("Third node", "Third body"),
            ("Third node -> Third First node", "Third First body"),
        ]

        assert len(expected_cards) == len(notes)

        for (title, body) in expected_cards:
            assert any(title == note.fields[0] and body == note.fields[1] for note in notes)


def test_math(tmp_path, data_folder):
    # Initalize convertor
    c = AnkiConvertor(exclude_empty=True)

    # Convert
    org_file = data_folder / "anki_math.org"
    out_file = tmp_path / "anki_math.apkg"
    c.convert(str(org_file), str(out_file))

    # Open the anki deck
    with open_apkg(str(out_file)) as col:

        notes = list(notes_iterator(col))

        expected_cards = [
            ("Mass–energy relation", "[$]E = mc^2[/$]"),
            ("Integers", "Let [$]a[/$] and [$]b[/$] be integers that are [$]\\le 0[/$]."),
        ]

        assert len(expected_cards) == len(notes)

        for (title, body) in expected_cards:
            assert any(title == note.fields[0] and body == note.fields[1] for note in notes)
