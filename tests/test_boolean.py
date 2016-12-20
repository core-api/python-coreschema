from schemarize.models import Boolean


def test_boolean_type():
    schema = Boolean()
    assert schema.validate(False) == []
    assert schema.validate(True) == []
    assert schema.validate(0) == [('Must be a boolean.', [])]
    assert schema.validate(1) == [('Must be a boolean.', [])]
