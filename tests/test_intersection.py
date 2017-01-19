from coreschema import Integer, String, Boolean


def test_intersection_of_types():
    # validate will never succeed in this case.
    schema = Integer() & String()
    assert schema.validate('abc') == [('Must be an integer.', [])]
    assert schema.validate(123) == [('Must be a string.', [])]


def test_intersection_of_intersections():
    # validate will never succeed in this case.
    schema = (Integer() & String()) & Boolean()
    assert schema.validate('abc') == [
        ('Must be an integer.', []),
        ('Must be a boolean.', [])
    ]
    assert schema.validate(123) == [
        ('Must be a string.', []),
        ('Must be a boolean.', [])
    ]


def test_intersection_of_type_restrictions():
    schema = Integer(multiple_of=3) & Integer(multiple_of=5)
    assert schema.validate(2) == [
        ('Must be a multiple of 3.', []),
        ('Must be a multiple of 5.', [])
    ]
    assert schema.validate(3) == [('Must be a multiple of 5.', [])]
    assert schema.validate(5) == [('Must be a multiple of 3.', [])]
    assert schema.validate(15) == []
