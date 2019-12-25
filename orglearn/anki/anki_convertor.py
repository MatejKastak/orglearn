import logging
import os
import random

import orgparse
import genanki

TEST_MODEL = genanki.Model(
  random.randrange(1 << 30, 1 << 31),
  'foomodel',
  fields=[
    {
      'name': 'AField',
    },
    {
      'name': 'BField',
    },
  ],
  templates=[
    {
      'name': 'card1',
      'qfmt': '{{AField}}',
      'afmt': '{{FrontSide}}'
              '<hr id="answer">'
              '{{BField}}',
    }
  ],
)


class AnkiConvertor():

    ANKI_EXT = '.apkg'

    def __init__(self, o_file, f_list, append=False):
        # TODO(mato): Implement append
        self.o_file = o_file
        self.f_list = f_list

        # Try to deteremine output file if none was specified
        if o_file is None:
            root, ext = os.path.splitext(os.path.basename(f_list[0]))
            o_file = root + AnkiConvertor.ANKI_EXT

        # Parse the org files into 1 tree
        cards = []
        for f in f_list:
            cur_file = orgparse.load(f)
            self._get_cards(cur_file, cards)

        self.anki(o_file, cards)

    def anki(self, anki_out_path, cards):
        my_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), anki_out_path)

        for c in cards:
            my_deck.add_note(c)

        genanki.Package(my_deck).write_to_file(anki_out_path)

    def _get_cards(self, tree_level, output_list):
        for c in tree_level.children:
            # TODO(mato): We can maybe include also cards that have children but
            # also have body text
            # TODO(mato): Node title should contain some info about ancestor nodes
            # TODO(mato): This node will also contain the child node titles
            if not c.children:
                output_list.append(genanki.Note(model=TEST_MODEL, fields=[c.heading, c.body]))
            self._get_cards(c, output_list)
