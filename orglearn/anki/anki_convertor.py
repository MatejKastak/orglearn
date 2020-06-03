import os
import random
import re
import typing

import genanki
import orgparse

TEST_MODEL = genanki.Model(
    random.randrange(1 << 30, 1 << 31),
    "foomodel",
    fields=[{"name": "AField",}, {"name": "BField",},],
    templates=[
        {
            "name": "card1",
            "qfmt": "{{AField}}",
            "afmt": "{{FrontSide}}" '<hr id="answer">' "{{BField}}",
        }
    ],
    css=".card {text-align: left;}",
)

latex_eq = re.compile(r"\$(.*)\$")
image_struct = re.compile(r"\[\[(.*)\]\]")


class AnkiConvertor:

    ANKI_EXT = ".apkg"

    def __init__(self, o_file, f_list, **kwargs):
        # TODO(mato): Implement append
        self.o_file = o_file
        self.f_list = f_list

        self.mobile = kwargs.pop("mobile", False)
        self.ignore_tags = set(kwargs.pop("ignore_tags_list", []))
        self.ignore_shallow_tags = set(kwargs.pop("ignore_shallow_tags_list", []))

        # Try to deteremine output file if none was specified
        # TODO(mato): This functionality can also be abstracted higher
        if o_file is None:
            root, _ = os.path.splitext(f_list[0])
            o_file = root + AnkiConvertor.ANKI_EXT

        # Parse the org files into 1 tree
        cards: typing.List[genanki.Note] = []
        for f in f_list:
            # TODO(mato): Don't allways set this as a new value instead we need
            # to mechanism to merge all trees into one big tree
            self.cur_file = orgparse.load(f)
            self._get_cards(self.cur_file, cards)

        self.anki(o_file, cards)

    def anki(self, anki_out_path, cards):
        # TODO(mato): This method can be abstracted as staticmethod
        try:
            # Try to set the deck name to a org file title comment
            deck_name = self.cur_file._special_comments["TITLE"][0]
        except KeyError:
            deck_name = anki_out_path

        my_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), anki_out_path)

        for c in cards:
            my_deck.add_note(c)

        genanki.Package(my_deck).write_to_file(anki_out_path)

    def _get_cards(self, tree_level, output_list: typing.List[genanki.Note]):
        for child in tree_level.children:
            # TODO(mato): We can maybe include also cards that have children but
            # also have body text, those will have a list of all children titles?
            # TODO(mato): This node will also contain the child node titles
            if not self.ignore_tags.intersection(
                child.tags
            ) and not self.ignore_shallow_tags.intersection(child.shallow_tags):
                self._process_node(child, output_list)
            self._get_cards(child, output_list)

    @staticmethod
    def _get_card_title(node: orgparse.node.OrgNode, depth: int = 1) -> str:
        """Construct the node title with the optional parent node headings."""
        res = node.heading
        for _ in range(depth):
            try:
                node = node.parent
                res = "{} -> {}".format(node.heading, res)
            except AttributeError:
                return res
        return res

    def _process_node(
        self, node: orgparse.node.OrgNode, output_list: typing.List[genanki.Note]
    ) -> None:
        """Process a single node and append a new Note."""
        generate = False
        card_body = ""
        depth = 1
        if node.body or not node.children:
            generate = True
            card_body = node.body

            # Ignore processing if the output is for mobile
            if not self.mobile:
                card_body = latex_eq.sub(r"[$]\1[/$]", card_body)
                card_body = image_struct.sub(r'<img src="\1">', card_body)

            # Check if the parent is list, if so increase the card_title depth
            try:
                # TODO: Walk the list and find all parent lists
                if "anki_list" in node.parent.shallow_tags:
                    depth = 2
            except AttributeError:
                pass

        if "anki_list" in node.shallow_tags:
            generate = True

            if card_body:
                card_body += "\n"

            for child in node.children:
                card_body += "- {}\n".format(child.heading)

        card_body = card_body.replace("\n", "<br />")
        card_title = self._get_card_title(node, depth)
        if generate:
            output_list.append(genanki.Note(model=TEST_MODEL, fields=[card_title, card_body]))
