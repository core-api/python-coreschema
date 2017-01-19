from coreschema import Integer


def test_not():
    schema = ~Integer()
    assert schema.validate('abc') == []
    assert schema.validate(123) == [('Must not match the option.', [])]


def test_complex_not():
    schema = Integer() & (~Integer(multiple_of=3) & ~Integer(multiple_of=5))
    assert schema.validate('') == [('Must be an integer.', [])]
    assert schema.validate(2) == []
    assert schema.validate(3) == [('Must not match the option.', [])]
    assert schema.validate(5) == [('Must not match the option.', [])]
