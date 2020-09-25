import re
import orgparse
import typing
import os

# TODO: We should cache parsed files


class Preprocessor:
    REGEXP_IMAGE = re.compile(r"^\s*\[\[(.*)\]\]$")
    REGEXP_COMMAND = re.compile(r"^\*+\s+\[([A-Z]+)\](.*)$")

    def __init__(self) -> None:
        self.source_file: typing.Optional[str] = None

    def preprocess_file(self, file_path: str) -> str:
        with open(file_path, "r") as input_file:
            self.current_file = file_path
            return self.preprocess_string(input_file.read())

    def preprocess_string(self, file_source: str) -> str:
        res = ""

        for line in file_source.splitlines():
            m = self.REGEXP_COMMAND.search(line)

            # TODO: This can be optimized

            if m:
                if m.group(1) == "OL":
                    parts = m.group(2).split("@")
                    if len(parts) == 1:
                        include_title = parts[0]
                        include_path = self.current_file
                    else:
                        include_title = parts[0]
                        include_path = parts[1] or self.current_file

                    res += line
                    res += "\n"

                    include_org_file = orgparse.load(include_path)
                    self.current_file = include_path

                    for something in include_org_file:
                        try:
                            if something.heading == include_title:
                                res += self._process_body(something._lines[1:])
                                res += "\n"
                                for child in something.children:
                                    res += self._include_node(child)
                        except AttributeError:
                            # Root node does not have heading attribute
                            pass
                elif m.group(1) == "OI":
                    parts = m.group(2).split("@")
                    if len(parts) == 1:
                        include_title = parts[0]
                        include_path = self.current_file
                    else:
                        include_title = parts[0]
                        include_path = parts[1] or self.current_file

                    # res += line
                    res += "\n"

                    include_org_file = orgparse.load(include_path)
                    self.current_file = include_path

                    for something in include_org_file:
                        try:
                            if something.heading == include_title:
                                res += self._process_body(something._lines[1:])
                                res += "\n"
                                for child in something.children:
                                    res += self._include_node(child)
                        except AttributeError:
                            # Root node does not have heading attribute
                            pass
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
        res += node._lines[0]
        res += "\n"
        res += self._process_body(node._lines[1:])
        # res += node.body
        res += "\n"

        for child in node.children:
            res += self._include_node(child)

        return res
