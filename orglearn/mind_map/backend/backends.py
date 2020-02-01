from orglearn.mind_map.backend.graphviz import Graphviz


class Backends:

    BACKENDS = {}
    INSTANCES = {}

    @staticmethod
    def register_backend(b, s=None):
        # TODO: The name of the class is incorent and alway abcmeta
        Backends.BACKENDS[s or b.__class__.__name__.lower()] = b

    @staticmethod
    def get_backends():
        return Backends.BACKENDS.keys()

    @staticmethod
    def get_default_backend():
        return "graphviz"

    @staticmethod
    def make(backend_string, *args, **kwargs):

        try:
            return Backends.INSTANCES[backend_string]
        except KeyError:
            return Backends._instantiate(backend_string, *args, **kwargs)

    @staticmethod
    def _instantiate(backend_string, *args, **kwargs):
        assert backend_string in Backends.BACKENDS.keys()
        Backends.INSTANCES[backend_string] = Backends.BACKENDS[backend_string](
            *args, **kwargs
        )
        return Backends.INSTANCES[backend_string]


# Register all backends here
Backends.register_backend(Graphviz, "graphviz")
