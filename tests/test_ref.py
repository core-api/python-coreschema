import coreschema


def test_ref():
    child = coreschema.Object(
        properties={
            'a': coreschema.String(),
            'b': coreschema.Integer()
        }
    )
    schema = coreschema.Ref('Child')
    context = {'refs': {'Child': child}}

    assert schema.validate({'a': 'abc', 'b': 123}, context) == []
    assert schema.validate({'a': 'abc', 'b': 'abc'}, context) == [('Must be an integer.', ['b'])]


def test_ref_space():
    schema = coreschema.RefSpace(
        refs={
            'PositiveInteger': coreschema.Integer(minimum=1),
            'Root': coreschema.Ref('PositiveInteger') | coreschema.String()
        },
        root='Root'
    )

    assert schema.validate(1) == []
    assert schema.validate('abc') == []
    assert schema.validate(0) == [('Must match one of the options.', [])]
