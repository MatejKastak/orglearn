import os
import re
import sys
import typing

import orgparse

# TODO: We should cache parsed files


class Preprocessor:
    REGEXP_IMAGE = re.compile(r"^\s*\[\[(.*)\]\]$")
    REGEXP_COMMAND = re.compile(r"^\*+\s+\[([A-Z]+)\](.*)$")

    def __init__(self) -> None:
        self.source_file: typing.Optional[str] = None

    def preprocess_file(self, file_path: str) -> str:
        with open(file_path, "r") as input_file:
            self.origin_file = file_path
            self.current_file = file_path
            return self.preprocess_string(input_file.read())

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
                            # Not unique
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
                            # Not unique
                            return None
                        else:
                            ret_node = node
                except AttributeError:
                    # Root node does not have heading attribute, ignore it
                    pass

        return ret_node

    def preprocess_string(self, file_source: str) -> str:
        res = ""

        for line_num, line in enumerate(file_source.splitlines(), start=1):
            m = self.REGEXP_COMMAND.search(line)

            # TODO: This can be optimized

            if m:
                if m.group(1) == "OL":
                    parts = m.group(2).split("@")
                    if len(parts) == 1:
                        include_title = parts[0]
                        include_path = self.origin_file
                    else:
                        include_title = parts[0]
                        include_path = parts[1] or self.origin_file

                    res += line
                    res += "\n"

                    include_org_file = orgparse.load(include_path)
                    self.current_file = include_path

                    node = self._find_node_in_tree(include_title, include_org_file)
                    if node is None:
                        # TODO: Abort
                        # TODO: Should we raise exception
                        self._abort_preprocessing(include_title, line_num)
                        return ""

                    res += self._process_body(node._lines[1:])
                    res += "\n"
                    for child in node.children:
                        res += self._include_node(child)
                elif m.group(1) == "OI":
                    parts = m.group(2).split("@")
                    if len(parts) == 1:
                        include_title = parts[0]
                        include_path = self.origin_file
                    else:
                        include_title = parts[0]
                        include_path = parts[1] or self.origin_file

                    # Don't include the node title
                    # res += line
                    res += "\n"

                    include_org_file = orgparse.load(include_path)
                    self.current_file = include_path

                    node = self._find_node_in_tree(include_title, include_org_file)
                    if node is None:
                        # TODO: Abort
                        # TODO: Should we raise exception
                        self._abort_preprocessing(include_title, line_num)
                        return ""

                    res += self._process_body(node._lines[1:])
                    res += "\n"
                    for child in node.children:
                        res += self._include_node(child)
                elif m.group(1) == "OIS":
                    parts = m.group(2).split("@")
                    if len(parts) == 1:
                        include_title = parts[0]
                        include_path = self.origin_file
                    else:
                        include_title = parts[0]
                        include_path = parts[1] or self.origin_file

                    # Don't include the node title
                    # res += line
                    res += "\n"

                    include_org_file = orgparse.load(include_path)
                    self.current_file = include_path

                    node = self._find_node_in_tree(include_title, include_org_file)
                    if node is None:
                        # TODO: Abort
                        # TODO: Should we raise exception
                        self._abort_preprocessing(include_title, line_num)
                        return ""

                    res += self._process_body(node._lines[1:])
                    res += "\n"
                    # for child in node.children:
                    #     res += self._include_node(child)
                else:
                    # This branch is here in case any of the titles start with [TAG] prefix
                    res += line
                    res += "\n"
            else:
                res += line
                res += "\n"

        return res

    def _process_body(self, body: typing.List[str]) -> str:
        res = ""
        for line in body:
            m = self.REGEXP_IMAGE.search(line)

            if m:
                processed_file_base_dir = os.path.dirname(self.current_file)
                res_image_path = os.path.join(processed_file_base_dir, m.group(1))
                res_image_path = os.path.normpath(res_image_path)

                res += "[[./{}]]".format(res_image_path)
                res += "\n"
            else:
                res += line
                res += "\n"

        return res

    def _include_node(self, node: orgparse.node.OrgNode) -> str:
        res = ""

        # Get the heading line, this is a bit hackish, maybe a better way
        # is to construct the heading based on the public attributes
        # TODO: Adjust the number of stars (indent)
        res += node._lines[0]
        res += "\n"
        res += self._process_body(node._lines[1:])
        # res += node.body
        res += "\n"

        for child in node.children:
            res += self._include_node(child)

        return res

    def _abort_preprocessing(self, node_id: str, line_num: int) -> None:
        print(
            'Preprocessing file "{}" failed when searching for node_id "{}" in file "{}" referenced from "{}":{}'.format(
                self.origin_file, node_id, self.current_file, self.origin_file, line_num
            )
        )
        sys.exit(1)
