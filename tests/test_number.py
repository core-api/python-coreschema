from coreschema import Number, Integer


def test_number_type():
    schema = Number()
    assert schema.validate(1) == []
    assert schema.validate(1.0) == []
    assert schema.validate('a') == [('Must be a number.', [])]


def test_integer_type():
    schema = Integer()
    assert schema.validate(1) == []
    assert schema.validate(1.0) == []
    assert schema.validate(1.5) == [('Must be an integer.', [])]
    assert schema.validate(True) == [('Must be an integer.', [])]


def test_minimum():
    schema = Number(minimum=3.0)
    assert schema.validate(4) == []
    assert schema.validate(3) == []
    assert schema.validate(2) == [('Must be greater than or equal to 3.0.', [])]
    assert schema.validate(3.5) == []
    assert schema.validate(3.0) == []
    assert schema.validate(2.5) == [('Must be greater than or equal to 3.0.', [])]


def test_exclusive_minimum():
    schema = Number(minimum=3.0, exclusive_minimum=True)
    assert schema.validate(4) == []
    assert schema.validate(3) == [('Must be greater than 3.0.', [])]
    assert schema.validate(2) == [('Must be greater than 3.0.', [])]
    assert schema.validate(3.5) == []
    assert schema.validate(3.0) == [('Must be greater than 3.0.', [])]
    assert schema.validate(2.5) == [('Must be greater than 3.0.', [])]


def test_maximum():
    schema = Number(maximum=3.0)
    assert schema.validate(4) == [('Must be less than or equal to 3.0.', [])]
    assert schema.validate(3) == []
    assert schema.validate(2) == []
    assert schema.validate(3.5) == [('Must be less than or equal to 3.0.', [])]
    assert schema.validate(3.0) == []
    assert schema.validate(2.5) == []


def test_exclusive_maximum():
    schema = Number(maximum=3.0, exclusive_maximum=True)
    assert schema.validate(4) == [('Must be less than 3.0.', [])]
    assert schema.validate(3) == [('Must be less than 3.0.', [])]
    assert schema.validate(2) == []
    assert schema.validate(3.5) == [('Must be less than 3.0.', [])]
    assert schema.validate(3.0) == [('Must be less than 3.0.', [])]
    assert schema.validate(2.5) == []


def test_multiple_of():
    schema = Number(multiple_of=0.5)
    assert schema.validate(2) == []
    assert schema.validate(2.0) == []
    assert schema.validate(2.1) == [('Must be a multiple of 0.5.', [])]

    schema = Number(multiple_of=2)
    assert schema.validate(2) == []
    assert schema.validate(4) == []
    assert schema.validate(6.0) == []
    assert schema.validate(3) == [('Must be a multiple of 2.', [])]
    assert schema.validate(3.0) == [('Must be a multiple of 2.', [])]
