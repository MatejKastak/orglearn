import enum
import logging
import random
import re
import typing

import genanki
import orgparse

latex_eq = re.compile(r"\$(.*)\$")
image_struct = re.compile(r"\[\[(.*)\]\]")


class AnkiConvertMode(enum.Enum):
    """Mode of conversion."""

    NORMAL = enum.auto()
    BRIEF = enum.auto()
    CODE = enum.auto()


class NodeConvertor:
    """Convert orglearn node to anki Note."""

    MODEL_NORMAL = genanki.Model(
        # TODO: Abstract the id
        random.randrange(1 << 30, 1 << 31),
        "Orglearn - normal",
        fields=[{"name": "AField"}, {"name": "BField"}],
        templates=[
            {
                "name": "card1",
                "qfmt": "{{AField}}",
                "afmt": "{{FrontSide}}" '<hr id="answer">' "{{BField}}",
            }
        ],
        css=".card {text-align: left;}",
    )

    MODEL_CODE = genanki.Model(
        # TODO: Abstract the id
        random.randrange(1 << 30, 1 << 31),
        "Orglearn - code",
        fields=[{"name": "Task"}, {"name": "Assignment"}, {"name": "Solution"}],
        templates=[
            {
                "name": "card1",
                "qfmt": "{{Task}}" "</br>" "{{Assignment}}",
                "afmt": "{{FrontSide}}" '<hr id="answer">' "{{Solution}}",
            }
        ],
        css=".card {text-align: left;}",
    )

    def __init__(self, mobile: bool = False):
        self._mobile = mobile
        self._mode_convertors = {
            AnkiConvertMode.NORMAL: self._convert_normal,
            AnkiConvertMode.BRIEF: self._convert_brief,
            AnkiConvertMode.CODE: self._convert_code,
        }

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

    def convert(
        self, node: orgparse.node.OrgNode, mode: AnkiConvertMode = AnkiConvertMode.NORMAL
    ) -> typing.Optional[genanki.Note]:
        """Process a single node and append a new Note."""
        try:
            return self._mode_convertors[mode](node)
        except KeyError:
            logging.error("Invalid convertor mode selected")
            return None

    def _convert_normal(self, node: orgparse.node.OrgNode) -> typing.Optional[genanki.Note]:
        generate = False
        card_body = ""
        depth = 1
        if node.body or not node.children:
            generate = True
            card_body = node.body

            # Ignore processing if the output is for mobile
            if not self._mobile:
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
            return genanki.Note(model=self.MODEL_NORMAL, fields=[card_title, card_body])

        return None

    def _convert_brief(self, node: orgparse.node.OrgNode) -> typing.Optional[genanki.Note]:
        return None

    def _convert_code(self, node: orgparse.node.OrgNode) -> typing.Optional[genanki.Note]:
        generate = False
        depth = 1
        assignment = ""
        solution = node.body
        if node.body or not node.children:
            generate = True

            # Split the node body into two parts beaking on the first 2 empty lines
            body_split = node.body.split("\n\n\n", 1)
            if len(body_split) == 2:
                assignment, solution = body_split

            # Ignore processing if the output is for mobile
            if not self._mobile:
                assignment = latex_eq.sub(r"[$]\1[/$]", assignment)
                assignment = image_struct.sub(r'<img src="\1">', assignment)
                solution = latex_eq.sub(r"[$]\1[/$]", solution)
                solution = image_struct.sub(r'<img src="\1">', solution)

            # Check if the parent is list, if so increase the card_title depth
            try:
                # TODO: Walk the list and find all parent lists
                if "anki_list" in node.parent.shallow_tags:
                    depth = 2
            except AttributeError:
                pass

        if "anki_list" in node.shallow_tags:
            generate = True

            if solution:
                solution += "\n"

            for child in node.children:
                solution += "- {}\n".format(child.heading)

        assignment = assignment.replace("\n", "<br />")
        solution = solution.replace("\n", "<br />")
        card_title = self._get_card_title(node, depth)
        if generate:
            return genanki.Note(model=self.MODEL_CODE, fields=[card_title, assignment, solution])

        return None
