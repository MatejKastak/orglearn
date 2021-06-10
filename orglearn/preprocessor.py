import logging
import pathlib
import re
import sys
import typing

import orgparse

import orglearn.utils as utils

# TODO: We should cache parsed files

log = logging.getLogger(__name__)


class Preprocessor:
    REGEXP_IMAGE = re.compile(r"^\s*\[\[(.*)\]\]$")
    REGEXP_COMMAND = re.compile(r"^(?P<stars>\*+)\s+\[(?P<command>[A-Z]+)\](?P<args>.*)$")

    def __init__(self) -> None:
        self.source_file: typing.Optional[str] = None

    def preprocess_file(self, file_path: str) -> str:
        """Preprocess file specified by the path."""
        log.info(f"Preprocessing file {file_path}")

        f = pathlib.Path(file_path)

        with utils.Workdir(f.parent):
            self.origin_file = pathlib.Path(f.name)
            self.current_file = file_path
            return self.preprocess_string(self.origin_file.read_text())

    @staticmethod
    def _find_node_in_tree(
        node_id: str, tree: orgparse.node.OrgNode
    ) -> typing.Optional[orgparse.node.OrgNode]:
        """Find node in the orgfile based on the node_id.

        Return `None` if node is not found or the node is not unique. If
        the `node_id` starts with '&' match on the 'ID' org property.
        """
        ret_node: orgparse.node.OrgNode = None
        node_id = node_id.strip()

        for node in tree:
            if node_id.startswith("&"):
                # Check the reference
                try:
                    # Strip the '&' prefix
                    match_string = node_id[1:]

                    if node.get_property("ID") == match_string:
                        if ret_node is not None:
                            log.warning(f"Node is not unique {node_id}")
                            return None
                        else:
                            ret_node = node
                except AttributeError:
                    # Root node does not have heading attribute, ignore it
                    pass
            else:
                try:
                    if node.heading == node_id:
                        if ret_node is not None:
                            log.warning(f"Node is not unique {node_id}")
                            return None
                        else:
                            ret_node = node
                except AttributeError:
                    # Root node does not have heading attribute, ignore it
                    pass

        return ret_node

    def preprocess_string(self, file_source: str) -> str:
        res = ""

        for line_num, line in enumerate(file_source.splitlines(keepends=True), start=1):
            m = self.REGEXP_COMMAND.search(line)

            if m:
                next_level = len(m.group("stars")) + 1
                command = m.group("command")

                parts = m.group("args").split("@")
                if len(parts) == 1:
                    include_title = parts[0]
                    include_path = self.origin_file
                else:
                    include_title = parts[0]
                    include_path = parts[1] or self.origin_file

                include_org_file = orgparse.load(str(include_path))
                self.current_file = include_path

                if command == "OL":
                    res += line

                    node = self._find_node_in_tree(include_title, include_org_file)
                    if node is None:
                        self._abort_preprocessing(include_title, line_num)
                        return ""

                    res += self._process_body(node._lines[1:])
                    for child in node.children:
                        res += self._include_node(next_level, child)
                elif command == "OI":

                    node = self._find_node_in_tree(include_title, include_org_file)
                    if node is None:
                        self._abort_preprocessing(include_title, line_num)
                        return ""

                    res += self._process_body(node._lines[1:])
                    for child in node.children:
                        res += self._include_node(next_level, child)
                elif command == "OIS":

                    node = self._find_node_in_tree(include_title, include_org_file)
                    if node is None:
                        self._abort_preprocessing(include_title, line_num)
                        return ""

                    res += self._process_body(node._lines[1:])
                else:
                    # This branch is here in case any of the titles start with [TAG] prefix
                    res += line
            else:
                res += line

        return res

    def _process_body(self, body: typing.List[str]) -> str:
        res = ""
        for line in body:
            m = self.REGEXP_IMAGE.search(line)

            if m:
                processed_file_base_dir = pathlib.Path(self.current_file).parent
                res_image_path = processed_file_base_dir / m.group(1)
                res_image_path = res_image_path.resolve(strict=True)

                if res_image_path.suffix not in [".png", ".jpg"]:
                    log.warning(
                        f"Image {res_image_path} might not be supported (consider converting to .png)"
                    )

                res += f"[[{str(res_image_path)}]]"
                res += "\n"
            else:
                res += line
                res += "\n"

        return res

    def _include_node(self, base_level: int, node: orgparse.node.OrgNode) -> str:
        res = ""

        # Get the heading line, this is a bit hackish, maybe a better way
        # is to construct the heading based on the public attributes
        heading = node._lines[0]

        # Strip the heading level and construct a new one
        heading = heading.lstrip("*")

        # Construct the correct heading
        res += "*" * base_level
        res += heading

        res += "\n"

        res += self._process_body(node._lines[1:])

        for child in node.children:
            res += self._include_node(base_level + 1, child)

        return res

    def _abort_preprocessing(self, node_id: str, line_num: int) -> None:
        # TODO: Replace this function with exception
        print(
            'Preprocessing file "{}" failed when searching for node_id "{}" in file "{}" referenced from "{}":{}'.format(
                self.origin_file, node_id, self.current_file, self.origin_file, line_num
            )
        )
        sys.exit(1)
