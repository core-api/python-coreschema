from coreschema import Union, Integer, String, Boolean


def test_union_of_types():
    schema = Integer() | String()
    assert schema.validate('abc') == []
    assert schema.validate(123) == []
    assert schema.validate(True) == [('Must match one of the options.', [])]

def test_union_of_unions():
    schema = (Integer() | String()) | Boolean()
    assert schema.validate('abc') == []
    assert schema.validate(123) == []
    assert schema.validate(True) == []
    assert schema.validate({}) == [('Must match one of the options.', [])]

    schema = Integer() | (String() | Boolean())
    assert schema.validate('abc') == []
    assert schema.validate(123) == []
    assert schema.validate(True) == []
    assert schema.validate({}) == [('Must match one of the options.', [])]
