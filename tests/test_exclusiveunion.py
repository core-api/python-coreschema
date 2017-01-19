from coreschema import Integer, String, Boolean


def test_xor_of_types():
    schema = Integer() ^ String()
    assert schema.validate('abc') == []
    assert schema.validate(123) == []
    assert schema.validate(True) == [('Must match one of the options.', [])]


def test_xor_of_type_restrictions():
    schema = Integer(multiple_of=3) ^ Integer(multiple_of=5)
    assert schema.validate(2) ==  [('Must match one of the options.', [])]
    assert schema.validate(3) == []
    assert schema.validate(5) == []
    assert schema.validate(15) ==  [('Must match only one of the options.', [])]
