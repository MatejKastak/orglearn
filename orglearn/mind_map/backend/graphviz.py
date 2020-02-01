from orglearn.mind_map.backend.backend import Backend

import graphviz


class Graphviz(Backend):
    def __init__(self, *args, **kwargs):
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
        tree.root.heading = "FILENAME?"
        self._process_node(tree.root)

        # TODO(mato): Add option to split on highest level into files

        # TODO(mato): Cannot take stream
        self.dot.render("test-mmap.gv", view=True)

    def _process_node(self, tree_node):

        # TODO(mato): What to do with a node body

        # First construct the current node
        self.dot.node(tree_node.heading, tree_node.heading)

        # If node has a parrent, create a link to it
        if tree_node.parent is not None:
            self.dot.edge(
                tree_node.parent.heading, tree_node.heading
            )  # , constraint='false')

        # Process all children of this node
        for c in tree_node.children:
            # TODO(mato): Are these TODOs even relevant?
            # TODO(mato): This node will also contain the child node headings
            # TODO(mato): Create better identification
            # TODO(mato): Node name cannot contain ':'
            if not self.ignore_tags.intersection(c.tags):
                self._process_node(c)

    def get_ext(self):
        return ".png"
