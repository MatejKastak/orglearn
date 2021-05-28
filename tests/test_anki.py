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
            "First node",
            "First node -> First First node",
            "Second node",
            "Third node",
            "Third node -> Third First node",
        ]

        for title in expected_cards:
            assert any(title in note.fields[0] for note in notes)
