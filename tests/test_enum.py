from coreschema import Enum


def test_enum():
    schema = Enum(['abc', 'def'])
    assert schema.validate('def') == []
    assert schema.validate('ghi') == [("Must be one of ['abc', 'def'].", [])]


def test_enum_exact():
    schema = Enum(['abc'])
    assert schema.validate('abc') == []
    assert schema.validate('def') == [("Must be 'abc'.", [])]
