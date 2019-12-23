import abc

class Backend(abc.ABC):

    @abc.abstractmethod
    def convert(self, tree, file_path, **kwargs):
        ...
