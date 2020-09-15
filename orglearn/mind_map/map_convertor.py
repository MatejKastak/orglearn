import os

import orgparse
from orglearn.preprocessor import Preprocessor


class MapConvertor:
    def __init__(self, o_file, f_list, backend, **kwargs):

        # TODO(mato): This method is duplicate
        # Try to deteremine output file if none was specified
        if o_file is None:
            root, ext = os.path.splitext(f_list[0])
            o_file = root + backend.get_ext()

        # Parse the org files into 1 tree
        # TODO(mato): For now we are expecting only one file, make it more generic
        for f in f_list[:1]:
            source = Preprocessor().preprocess_file(f)
            tree = orgparse.loads(source)

            with open(o_file, "w") as o_stream:
                backend.convert(tree, o_stream, **kwargs)
