import logging
import pathlib
import random
import typing

import genanki
import orgparse
from anki.exporting import AnkiPackageExporter
from anki.importing import AnkiPackageImporter

import orglearn.utils as utils
from orglearn.anki.node_convertor import AnkiConvertMode, NodeConvertor
from orglearn.preprocessor import Preprocessor

log = logging.getLogger(__name__)


class AnkiConvertor:
    """Org to Anki convertor."""

    ANKI_EXT = ".apkg"

    COMMENT_ANKI_CONVERT_MODE = "ANKI_CONVERT_MODE"

    def __init__(self, **kwargs: typing.Any):
        self.exclude_empty = kwargs.pop("exclude_empty", False)
        self.ignore_tags = set(kwargs.pop("ignore_tags_list", {}))
        self.ignore_shallow_tags = set(kwargs.pop("ignore_shallow_tags_list", {}))
        self._convert_mode = kwargs.pop("convert_mode", None)
        self.user_supplied_convert_mode = bool(self._convert_mode)

        if kwargs:
            # If we have unused options raise an exception
            ValueError(f"Unknown kwargs '{kwargs}'")

        self.node_convertor = NodeConvertor()
        self.preprocessor = Preprocessor()

    def convert(self, in_file_str: str, out_file_str: str = None) -> None:
        """Convert a single file to ANKI deck."""

        log.info(f"Converting file '{in_file_str}' to ANKI deck @ '{out_file_str}'")

        # Create paths
        in_file = pathlib.Path(in_file_str)
        if out_file_str is not None:
            assert out_file_str.endswith(AnkiConvertor.ANKI_EXT)
            out_file = pathlib.Path(out_file_str).resolve()
        else:
            out_file = in_file.with_suffix(AnkiConvertor.ANKI_EXT).resolve()
        tmp_out_file = out_file.with_suffix(".tmp.apkg").resolve()

        # Convert the org nodes into list of Notes
        cards: typing.List[genanki.Note] = []

        # Preprocess and parse the file
        preprocessed_source = self.preprocessor.preprocess_file(str(in_file))
        org_file = orgparse.loads(preprocessed_source)

        # If user did not supplied the convert mode - try to get the convert mode
        # from the org file header fall back to NORMAL mode
        if not self.user_supplied_convert_mode:
            try:
                self.convert_mode = AnkiConvertMode[
                    org_file._special_comments[self.COMMENT_ANKI_CONVERT_MODE][0].upper()
                ]
            except KeyError:
                self.convert_mode = AnkiConvertMode.NORMAL
        else:
            self.convert_mode = self._convert_mode

        self._get_cards(org_file, cards)

        # Try to set the deck name to a org file title comment
        try:
            deck_name = org_file._special_comments["TITLE"][0]
        except (KeyError, IndexError):
            deck_name = out_file.stem

        # TODO: Hash should be calculated from the cards
        deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)

        for c in cards:
            deck.add_note(c)

        package = genanki.Package(deck)
        package.media_files = self.node_convertor.media_files
        package.write_to_file(str(tmp_out_file))

        # Import and export the collection using Anki
        # This is neccessary to make mobile version work (include rendered equations)
        with utils.create_empty_anki_collection() as col:
            log.debug("Importing to tmp ANKI collection")
            imp = AnkiPackageImporter(col, str(tmp_out_file))
            imp.run()
            log.debug("Exporting from tmp ANKI collection")
            exp = AnkiPackageExporter(col)
            exp.exportInto(str(out_file))

        tmp_out_file.unlink()

    def _get_cards(
        self, tree_level: orgparse.node.OrgNode, output_list: typing.List[genanki.Note]
    ) -> None:
        for child in tree_level.children:
            # TODO: We can maybe include also cards that have children but
            # also have body text, those will have a list of all children titles?
            # TODO: This node will also contain the child node titles
            if self.should_include_node(child):
                self._process_node(child, output_list)
            self._get_cards(child, output_list)

    def should_include_node(self, node: orgparse.node.OrgNode) -> bool:
        """Determine if the node should be included."""
        return not (
            bool(self.ignore_tags.intersection(node.tags))
            or bool(self.ignore_shallow_tags.intersection(node.shallow_tags))
            or (self.exclude_empty and not node.body.strip())
        )

    def _process_node(
        self, node: orgparse.node.OrgNode, output_list: typing.List[genanki.Note]
    ) -> None:
        converted_node = self.node_convertor.convert(node, self.convert_mode)
        if converted_node:
            log.info(f"Adding node '{node.heading}'")
            output_list.append(converted_node)
