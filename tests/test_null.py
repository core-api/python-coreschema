from coreschema import Null


def test_null_type():
    schema = Null()
    assert schema.validate(None) == []
    assert schema.validate(False) == [('Must be null.', [])]
    assert schema.validate(0) == [('Must be null.', [])]
