import pathlib

import pytest

from orglearn.preprocessor import Preprocessor


@pytest.fixture
def preprocessor():
    yield Preprocessor()


@pytest.fixture
def data_folder():
    yield pathlib.Path("./tests/data")
