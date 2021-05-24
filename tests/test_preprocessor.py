import orgparse


def test_no_preprocessing(preprocessor, data_folder):
    f = data_folder / "lokalne_prehladavanie.org"
    a = preprocessor.preprocess_file(str(f))
    b = f.read_text()

    assert a == b


def test_command_io(preprocessor, data_folder):
    f = data_folder / "oi.org"
    a = preprocessor.preprocess_file(str(f))
    b = orgparse.loads(a)

    expected = "\nThis tests the command OI\n\n\nThis should be duplicated\n\n"
    assert b.children[0].body == expected

    expected = "\n\nmore body"
    assert b.children[2].body == expected
