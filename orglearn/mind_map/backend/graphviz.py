from orglearn.mind_map.backend.backend import Backend

import graphviz


class Graphviz(Backend):
    def __init__(self, *args, **kwargs):
        self.ignore_shallow_tags = set(kwargs.get("ignore_shallow_tags_list", []))
        self.ignore_tags = set(kwargs.get("ignore_tags_list", []))

    def convert(self, tree, stream, **kwargs):
        # TODO: Maybe create heading from file name
        # self.dot = graphviz.Digraph(comment='asd')
        self.dot = graphviz.Digraph(comment="asd")
        # self.dot.attr(size='6,6')
        # self.dot.attr('graph', size='8.3,11.7!')
        # self.dot.attr('graph', size='11.7,8.3!')
        # self.dot.attr('graph', page='8.3,11.7!')
        # self.dot.attr('graph', page='11.7,8.3!')
        # self.dot.attr('graph', ratio='auto')
        self.dot.attr("graph", ratio="scale")
        self.dot.attr("graph", overlap="false")
        # self.dot.attr('graph', mindist='5.0')
        self.dot.engine = "circo"
        # self.dot.attr('graph', ratio='0.2')
        # self.dot.attr('graph', K='100')
        # self.dot.attr('graph', maxiter='100')
        try:
            # Try to set the center node text to a org file title comment
            tree.root.heading = tree._special_comments["TITLE"][0]
        except KeyError:
            tree.root.heading = "MAP"

        self._process_node(tree.root)

        # TODO(mato): Add option to split on highest level into files

        # TODO(mato): Cannot take stream
        self.dot.render(stream.name)

    def _process_node(self, tree_node):
        """Create a map node from tree node and proccess its children."""

        # TODO(mato): What to do with a node body

        # First construct the current node
        self.dot.node(self._create_id(tree_node), tree_node.heading)

        # If node has a parrent, create a link to it
        if tree_node.parent is not None:
            self.dot.edge(
                self._create_id(tree_node.parent), self._create_id(tree_node)
            )  # , constraint='false')

        # Process all children of this node
        for c in tree_node.children:
            if not self.ignore_tags.intersection(c.tags):
                self._process_node(c)

    def _create_id(self, node):
        """Hash the node to create identifier to reference nodes."""
        try:
            return (
                self._normalize_heading(node.parent.heading)
                + "%"
                + str(node.level)
                + "%"
                + self._normalize_heading(node.heading)
            )
        except AttributeError:
            return str(node.level) + "%" + self._normalize_heading(node.heading)

    def _normalize_heading(self, heading):
        """Normalize heading for dot format. Essentialy remove all ':' from headings."""
        return heading.replace(":", "")

    def get_ext(self):
        # Graphviz automatically appends the '.pdf'
        # And we don't want to colide with `pdf` command so prepend the '-map'
        # This results in: "<filename>-map.pdf"
        return "-map"
