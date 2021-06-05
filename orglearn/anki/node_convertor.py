import enum
import logging
import pathlib
import random
import re
import typing

import genanki
import orgparse

log = logging.getLogger(__name__)

latex_eq = re.compile(r"\$\$?(.*?)\$\$?")
image_struct = re.compile(r"\[\[(.*?)\]\]")


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

    def __init__(self) -> None:
        self._mode_convertors = {
            AnkiConvertMode.NORMAL: self._convert_normal,
            AnkiConvertMode.BRIEF: self._convert_brief,
            AnkiConvertMode.CODE: self._convert_code,
        }

        self.media_files: typing.List[str] = []

    def _get_card_title(self, node: orgparse.node.OrgNode) -> str:
        """Construct the node title."""
        res = node.heading
        while 1:
            try:
                node = node.parent
                res = f"{node.heading} -> {res}"
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
            log.error("Invalid convertor mode selected")
            raise ValueError("Invalid convertor mode")

    def _convert_normal(self, node: orgparse.node.OrgNode) -> typing.Optional[genanki.Note]:
        generate = False
        card_body = ""
        node_body = "\n".join(node._lines[1:])
        if node_body or not node.children:
            generate = True
            card_body = self._convert_text_to_anki(node_body)

        if "anki_list" in node.shallow_tags:
            generate = True
            card_body = self._append_anki_list_footer(node, card_body)

        card_body = card_body.replace("\n", "<br />")
        card_title = self._get_card_title(node)
        if generate:
            return genanki.Note(model=self.MODEL_NORMAL, fields=[card_title, card_body])

        return None

    def _convert_brief(self, node: orgparse.node.OrgNode) -> typing.Optional[genanki.Note]:
        return None

    def _convert_code(self, node: orgparse.node.OrgNode) -> typing.Optional[genanki.Note]:
        generate = False
        assignment = ""
        solution = node.body
        node_body = "\n".join(node._lines[1:])
        if node_body or not node.children:
            generate = True

            # Split the node body into two parts beaking on the first 2 empty lines
            body_split = node_body.split("\n\n\n", 1)
            if len(body_split) == 2:
                assignment, solution = body_split

            assignment = self._convert_text_to_anki(assignment)
            solution = self._convert_text_to_anki(solution)

        if "anki_list" in node.shallow_tags:
            generate = True
            solution = self._append_anki_list_footer(node, solution)

        assignment = assignment.replace("\n", "<br />")
        solution = solution.replace("\n", "<br />")
        card_title = self._get_card_title(node)
        if generate:
            return genanki.Note(model=self.MODEL_CODE, fields=[card_title, assignment, solution])

        return None

    def _append_anki_list_footer(self, node: orgparse.node.OrgNode, body: str) -> str:
        """Generate footer for the nodes marked with :anki_list:.

        This footer will be a list of child nodes. The rationale is to provide aditional
        context for the nodes that are the list of some topics.
        """
        if body:
            body += "\n"

        for child in node.children:
            body += "- {}\n".format(child.heading)
        return body

    def _convert_text_to_anki(self, body: str) -> str:
        """Perform necessary adjustments to the card text."""
        res = ""
        for line in body.splitlines(keepends=True):

            # LaTeX
            line = latex_eq.sub(r"[$]\1[/$]", line)

            # Images
            match = image_struct.match(line)
            if match:
                line = image_struct.sub(
                    lambda x: f'<img src="{pathlib.Path(x.group(1)).name}">', line
                )
                # Collect the media files for exporting
                self.media_files.append(match.group(1))

            res += line

        return res
