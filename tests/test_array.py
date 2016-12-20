from coreschema import Array, String


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
