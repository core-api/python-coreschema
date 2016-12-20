from schemarize.models import Anything


def test_anything_type():
    schema = Anything()
    assert schema.validate([1, 2, 3]) == []
    assert schema.validate({'a': 1, 'b': True}) == []
    assert schema.validate(123) == []
    assert schema.validate(set()) == [('Must be a valid primitive type.', [])]
    assert schema.validate({1: 1}) == [('Object keys must be strings.', [])]
    assert schema.validate([1, 2, set()]) == [('Must be a valid primitive type.', [2])]
