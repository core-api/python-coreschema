from coreschema.encodings.jsonschema import jsonschema, load_jsonschema
import json
import os


LOCAL_DIR = os.path.dirname(__file__)
TESTS = [
    'additionalItems.json',
    'additionalProperties.json',
    'allOf.json',
    'anyOf.json',
    'default.json',
    # 'definitions.json',  # requires remote ref
    # 'dependancies.json',
    'enum.json',
    'items.json',
    'maximum.json',
    'maxItems.json',
    'maxLength.json',
    'maxProperties.json',
    'minimum.json',
    'minItems.json',
    'minLength.json',
    'minProperties.json',
    'multipleOf.json',
    # 'not.json',
    # 'oneOf.json',
    'pattern.json',
    'patternProperties.json',
    'properies.json',
    # ref, refRemote
    'required.json',
    'type.json',
    'uniqueItems.json',
]

def test_jsonschema():
    # Ensure that the JSON Schema metaschema validates.
    path = os.path.join(LOCAL_DIR, 'schema.json')
    data = json.load(open(path, 'rb'))

    assert jsonschema.validate(data) == []


def test_full_suite():
    testsuite_dir = os.path.join(LOCAL_DIR, 'testsuite')
    filenames = [
        os.path.join(testsuite_dir, filename)
        for filename in os.listdir(testsuite_dir)
        if os.path.isfile(os.path.join(testsuite_dir, filename))
            and filename in TESTS
    ]
    for filename in filenames:
        test_suites = json.load(open(filename, 'rd'))
        for test_suite in test_suites:
            assert jsonschema.validate(test_suite['schema']) == []
            schema = load_jsonschema(test_suite['schema'])
            for test_case in test_suite['tests']:
                data = test_case['data']
                expect_valid = test_case['valid']
                is_valid = schema.validate(data) == []
                assert is_valid == expect_valid, filename + ': ' + test_case['description']
