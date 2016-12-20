from schemarize.models import Object, String


def test_object_type():
    schema = Object()
    assert schema.validate({}) == []
    assert schema.validate({'a': 1}) == []
    assert schema.validate(1) == [('Must be an object.', [])]


def test_object_keys():
    schema = Object()
    assert schema.validate({}) == []
    assert schema.validate({'a': 1}) == []
    assert schema.validate({1: 1}) == [('Object keys must be strings.', [])]


def test_object_properties():
    schema = Object(properties={'name': String()})
    assert schema.validate({}) == []
    assert schema.validate({'name': ''}) == []
    assert schema.validate({'name': 1}) == [('Must be a string.', ['name'])]


def test_object_required():
    schema = Object(required=['name'])
    assert schema.validate({'name': 1}) == []
    assert schema.validate({}) == [('This field is required.', ['name'])]


def test_object_max_properties():
    schema = Object(max_properties=2)
    assert schema.validate({'a': 1, 'b': 2}) == []
    assert schema.validate({'a': 1, 'b': 2, 'c': 3}) == [('Must have no more than 2 properties.', [])]


def test_object_min_properties():
    schema = Object(min_properties=2)
    assert schema.validate({'a': 1, 'b': 2}) == []
    assert schema.validate({'a': 1}) == [('Must have at least 2 properties.', [])]


def test_object_empty():
    schema = Object(min_properties=1)
    assert schema.validate({'a': 1}) == []
    assert schema.validate({}) == [('Must not be empty.', [])]


def test_object_pattern_properties():
    schema = Object(pattern_properties={'^x-': String(max_length=3)})
    assert schema.validate({'foox-a': 1}) == []
    assert schema.validate({'x-foo': 1}) == [('Must be a string.', ['x-foo'])]


def test_object_additional_properties_as_boolean():
    schema = Object(properties={'a': String()}, additional_properties=False)
    assert schema.validate({'a': ''}) == []
    assert schema.validate({'b': ''}) == [('Invalid property.', ['b'])]


def test_object_additional_properties_as_schema():
    schema = Object(properties={'a': String()}, additional_properties=String())
    assert schema.validate({'a': ''}) == []
    assert schema.validate({'b': 1}) == [('Must be a string.', ['b'])]
