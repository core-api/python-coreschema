from coreschema import Array, String, Integer


def test_array_type():
    schema = Array()
    assert schema.validate([]) == []
    assert schema.validate(['a', 1]) == []
    assert schema.validate(1) == [('Must be an array.', [])]


def test_array_items():
    schema = Array(items=String())
    assert schema.validate([]) == []
    assert schema.validate(['a', 'b', 'c']) == []
    assert schema.validate(['a', 'b', 123]) == [('Must be a string.', [2])]


def test_array_items_as_list():
    schema = Array(items=[String(), Integer()])
    assert schema.validate([]) == []
    assert schema.validate(['a', 123]) == []
    assert schema.validate(['a', 'b']) == [('Must be an integer.', [1])]


def test_array_max_items():
    schema = Array(max_items=2)
    assert schema.validate([1, 2]) == []
    assert schema.validate([1, 2, 3]) == [('Must have no more than 2 items.', [])]


def test_array_min_items():
    schema = Array(min_items=2)
    assert schema.validate([1, 2]) == []
    assert schema.validate([1]) == [('Must have at least 2 items.', [])]


def test_array_empty():
    schema = Array(min_items=1)
    assert schema.validate([1]) == []
    assert schema.validate([]) == [('Must not be empty.', [])]


def test_array_unique_items():
    schema = Array(unique_items=True)
    assert schema.validate([1, 2, 3]) == []
    assert schema.validate([1, 2, 1]) == [('Must not contain duplicate items.', [])]


def test_array_additional_items_disallowed():
    schema = Array(items=[String(), Integer()])
    assert schema.validate(['a', 123, True]) == []

    schema = Array(items=[String(), Integer()], additional_items=False)
    assert schema.validate(['a', 123, True]) == [('Must have no more than 2 items.', [])]

    schema = Array(items=[String(), Integer()], additional_items=Integer())
    assert schema.validate(['a', 123, 'c']) == [('Must be an integer.', [2])]
