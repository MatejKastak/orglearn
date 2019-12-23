import abc

# TODO(mato): Consider moving changing this to Convertor base class
# it will have similiar interface, but it will output to the specified
# stream
class Backend(abc.ABC):

    @abc.abstractmethod
    def convert(self, tree, file_path, **kwargs):
        ...
