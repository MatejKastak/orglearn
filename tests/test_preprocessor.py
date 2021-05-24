def test_no_preprocessing(preprocessor, data_folder):
    f = data_folder / "lokalne_prehladavanie.org"
    a = preprocessor.preprocess_file(str(f))
    b = f.read_text()

    assert a == b
