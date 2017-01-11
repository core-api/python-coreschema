from coreschema import String


def test_string_type():
    schema = String()
    assert schema.validate('') == []
    assert schema.validate('abc') == []
    assert schema.validate(123) == [('Must be a string.', [])]


def test_max_length():
    schema = String(max_length=3)
    assert schema.validate('abc') == []
    assert schema.validate('abcd') == [('Must have no more than 3 characters.', [])]


def test_min_length():
    schema = String(min_length=3)
    assert schema.validate('abc') == []
    assert schema.validate('ab') == [('Must have at least 3 characters.', [])]


def test_blank():
    schema = String(min_length=1)
    assert schema.validate('abc') == []
    assert schema.validate('') == [('Must not be blank.', [])]


def test_pattern():
    schema = String(pattern='^a[0-9]$')
    assert schema.validate('a3') == []
    assert schema.validate('ab') == [('Must match the pattern /^a[0-9]$/.', [])]
    schema = String(pattern='a[0-9]')
    assert schema.validate('z a3 z') == []
    assert schema.validate('z ab z ') == [('Must match the pattern /a[0-9]/.', [])]


def test_format_email():
    schema = String(format='email')
    assert schema.validate('a@b') == []
    assert schema.validate('ab@') == [('Must be a valid email.', [])]


def test_format_uri():
    schema = String(format='uri')
    assert schema.validate('http://example.com') == []
    assert schema.validate('example.com') == [('Must be a valid uri.', [])]
