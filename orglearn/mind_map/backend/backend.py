import abc

# TODO(mato): Consider moving changing this to Convertor base class
# it will have similiar interface, but it will output to the specified
# stream
class Backend(abc.ABC):
    @abc.abstractmethod
    def convert(self, tree, o_stream, **kwargs):
        """Convert org tree with backend.
        Keyword Arguments:
        tree     -- Org tree input.
        o_stream -- Write output into the stream.
        **kwargs -- Optional arguments for backend.
        """
        ...

    def get_ext(self) -> str:
        raise NotImplemented()
