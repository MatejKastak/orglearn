from orglearn.mind_map.backend.backend import Backend

import graphviz

class Graphviz(Backend):

    def convert(self, tree, stream):
        import pdb; pdb.set_trace()
        # TODO: Maybe create heading from file name
        self.dot = graphviz.Digraph(comment='asd')
        self._process_node(tree.root)

    def anki(self, anki_out_path, cards):
        my_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), anki_out_path)

        for c in cards:
            my_deck.add_note(c)

        genanki.Package(my_deck).write_to_file(anki_out_path)

    def _process_node(self, tree_level):
        for c in tree_level.children:
            # TODO(mato): We can maybe include also cards that have children but
            # also have body text
            # TODO(mato): Node heading should contain some info about ancestor nodes
            # TODO(mato): This node will also contain the child node headings
            if not c.children:
                # output_list.append(genanki.Note(model=TEST_MODEL, fields=[c.heading, c.body]))
                # TODO(mato): Create better identification
                self.dot.node(c.heading, c.heading)

            self._process_node(c)

    def get_ext(self):
        return '.png'
