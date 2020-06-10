import os
import random
import typing

import genanki
import orgparse
from orglearn.anki.node_convertor import AnkiConvertMode, NodeConvertor


class AnkiConvertor:
    """Org to Anki convertor."""

    ANKI_EXT = ".apkg"

    COMMENT_ANKI_CONVERT_MODE = "ANKI_CONVERT_MODE"

    def __init__(self, o_file_path: str, f_list: typing.Sequence[str], **kwargs: typing.Any):
        # TODO: Implement append
        self.o_file_path = o_file_path
        self.f_list = f_list

        self.mobile = kwargs.pop("mobile", False)
        self.ignore_tags = set(kwargs.pop("ignore_tags_list", []))
        self.ignore_shallow_tags = set(kwargs.pop("ignore_shallow_tags_list", []))

        self._convert_mode = kwargs.pop("convert_mode", None)
        user_supplied_convert_mode = bool(self._convert_mode)

        self.node_convertor = NodeConvertor(self.mobile)

        # Try to deteremine output file if none was specified
        # TODO: This functionality can also be abstracted higher
        if o_file_path is None:
            root, _ = os.path.splitext(f_list[0])
            o_file_path = root + AnkiConvertor.ANKI_EXT

        # Convert the org files into list of notes
        cards: typing.List[genanki.Note] = []
        for f in f_list:
            self.cur_file = orgparse.load(f)

            # If user did not supplied the convert mode - try to get the convert mode
            # from the org file header fall back to NORMAL mode
            if not user_supplied_convert_mode:
                try:
                    self.convert_mode = AnkiConvertMode[
                        self.cur_file._special_comments[self.COMMENT_ANKI_CONVERT_MODE][0].upper()
                    ]
                except KeyError:
                    self.convert_mode = AnkiConvertMode.NORMAL
            else:
                self.convert_mode = self._convert_mode

            self._get_cards(self.cur_file, cards)

        self.anki(o_file_path, cards)

    def anki(self, anki_out_path: str, cards: typing.List[orgparse.node.OrgNode]) -> None:
        """Save the cards into the output file."""

        deck_name = anki_out_path

        # Try to set the deck name to a org file title comment
        try:
            deck_name = self.cur_file._special_comments["TITLE"][0]
        except KeyError:
            pass

        # TODO: Hash should be calculated from the cards
        my_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)

        for c in cards:
            my_deck.add_note(c)

        genanki.Package(my_deck).write_to_file(anki_out_path)

    def _get_cards(
        self, tree_level: orgparse.node.OrgNode, output_list: typing.List[genanki.Note]
    ) -> None:
        for child in tree_level.children:
            # TODO: We can maybe include also cards that have children but
            # also have body text, those will have a list of all children titles?
            # TODO: This node will also contain the child node titles
            if not self.ignore_tags.intersection(
                child.tags
            ) and not self.ignore_shallow_tags.intersection(child.shallow_tags):
                self._process_node(child, output_list)
            self._get_cards(child, output_list)

    def _process_node(
        self, node: orgparse.node.OrgNode, output_list: typing.List[genanki.Note]
    ) -> None:
        converted_node = self.node_convertor.convert(node, self.convert_mode)
        if converted_node:
            output_list.append(converted_node)
