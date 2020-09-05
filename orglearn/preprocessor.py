import re
import orgparse


def _include_node(node: orgparse.node.OrgNode) -> str:
    res = ""

    # Get the heading line, this is a bit hackish, maybe a better way
    # is to construct the heading based on the public attributes
    res += node._lines[0]
    res += "\n"
    res += node.body
    res += "\n"

    for child in node.children:
        res += _include_node(child)

    return res


def preprocess_string(file_source: str) -> str:
    res = ""

    for line in file_source.splitlines():
        m = re.search(r"^\*+\s+\[OL\](.*)$", line)

        if m:
            include_title, include_path = m.group(1).split("@")

            res += line

            include_org_file = orgparse.load(include_path)

            for something in include_org_file:
                try:
                    if something.heading == include_title:
                        res += something.body
                        res += "\n"
                        for child in something.children:
                            res += _include_node(child)
                except AttributeError:
                    # Root node does not have heading attribute
                    pass
        else:
            res += line
            res += "\n"

    return res


def preprocess_file(file_path: str) -> str:
    with open(file_path, "r") as input_file:
        return preprocess_string(input_file.read())
