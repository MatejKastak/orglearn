import orgparse


def test_no_preprocessing(preprocessor, data_folder):
    f = data_folder / "lokalne_prehladavanie.org"
    a = preprocessor.preprocess_file(str(f))
    b = f.read_text()

    assert a == b


def test_command_oi(preprocessor, data_folder):
    f = data_folder / "oi.org"
    a = preprocessor.preprocess_file(str(f))
    b = orgparse.loads(a)

    expected = "\nThis tests the command OI\n\n\nThis should be duplicated\n\n"
    assert b.children[0].body == expected

    expected = "\n\nmore body\n"
    assert b.children[2].body == expected

    assert b.children[3].body == "\n\ntest body\n"
    assert b.children[3].children[0].heading == "Nested"
    assert b.children[3].children[0].children[0].heading == "More"


def test_command_ois(preprocessor, data_folder):
    f = data_folder / "ois.org"
    a = preprocessor.preprocess_file(str(f))

    expected = """
* Main file

This tests the command OI


This should be duplicated


* Other heading

** Include me

This should be duplicated

* Testing header


more body

* Last header


test body

"""

    assert a == expected


def test_command_ol(preprocessor, data_folder):
    f = data_folder / "ol.org"
    a = preprocessor.preprocess_file(str(f))

    expected = """
* Main file

This tests the command OI

** [OL]Include me

This should be duplicated


* Other heading

** Include me

This should be duplicated

* Testing header

** [OL]More@./include.org

more body

* Last header

** [OL]Test@./include.org

test body

*** Nested

nested body

**** More

more body
"""
    assert a == expected


def test_invalid_command(preprocessor, data_folder):
    f = data_folder / "invalid_command.org"
    a = preprocessor.preprocess_file(str(f))

    expected = """
* Main file

This tests the command OI

** [ASD]Include me

* Other heading

** Include me

This should be duplicated

* Testing header

** [OL]More@./include.org

more body

* Last header

** [OL]Test@./include.org

test body

*** Nested

nested body

**** More

more body
"""

    assert a == expected
