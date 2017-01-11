import coreschema
import re


text_types = (str, unicode)


jsonschema = coreschema.RefSpace({
    'Schema': coreschema.Object(
        properties={
            # Meta
            'id': coreschema.String(format='uri'),
            '$schema': coreschema.String(format='uri'),
            'title': coreschema.String(),
            'description': coreschema.String(),
            'default': coreschema.Anything(),
            'definitions': coreschema.Ref('SchemaMap'),
            # Type
            'type': coreschema.Ref('SimpleTypes') | coreschema.Array(items=coreschema.Ref('SimpleTypes'), min_items=1, unique_items=True),
            # Number validators
            'minimum': coreschema.Number(),
            'maximum': coreschema.Number(),
            'exclusiveMinimum': coreschema.Boolean(default=False),
            'exclusiveMaximum': coreschema.Boolean(default=False),
            'multipleOf': coreschema.Number(minimum=0, exclusive_minimum=True),
            # String validators
            'minLength': coreschema.Integer(minimum=0, default=0),
            'maxLength': coreschema.Integer(minimum=0),
            'pattern': coreschema.String(format='regex'),
            'format': coreschema.String(),
            # Array validators
            'items': coreschema.Ref('Schema') | coreschema.Ref('SchemaArray'), # TODO: default={}
            'additionalItems': coreschema.Boolean() | coreschema.Ref('Schema'),  # TODO: default={}
            'minItems': coreschema.Integer(minimum=0, default=0),
            'maxItems': coreschema.Integer(minimum=0),
            'uniqueItems': coreschema.Boolean(default=False),
            # Object validators
            'properties': coreschema.Ref('SchemaMap'),
            'patternProperties': coreschema.Ref('SchemaMap'),
            'additionalProperties': coreschema.Boolean() | coreschema.Ref('Schema'),
            'minProperties': coreschema.Integer(minimum=0, default=0),
            'maxProperties': coreschema.Integer(minimum=0),
            'required': coreschema.Ref('StringArray'),
            'dependancies': coreschema.Object(additional_properties=coreschema.Ref('Schema') | coreschema.Ref('StringArray')),
            # Enum validators
            'enum': coreschema.Array(min_items=1, unique_items=True),
            # Composites
            'allOf': coreschema.Ref('SchemaArray'),
            'anyOf': coreschema.Ref('SchemaArray'),
            'oneOf': coreschema.Ref('SchemaArray'),
            'not': coreschema.Ref('Schema')
        },
        # dependancies=..., TODO
        default={},
    ),
    'SchemaArray': coreschema.Array(
        items=coreschema.Ref('Schema'),
        min_items=1,
    ),
    'SchemaMap': coreschema.Object(
        additional_properties=coreschema.Ref('Schema'),
        default={},
    ),
    'SimpleTypes': coreschema.Enum(
        enum=['array', 'boolean', 'integer', 'null', 'number', 'object', 'string']
    ),
    'StringArray': coreschema.Array(
        items=coreschema.String(),
        min_items=1,
        unique_items=True,
    )
}, root='Schema')


KEYWORD_TO_TYPE = {
    'minimum': ['number', 'integer'],
    'maximum': ['number', 'integer'],
    'exclusiveMinimum': ['number', 'integer'],
    'exclusiveMaximum': ['number', 'integer'],
    'multipleOf': ['number', 'integer'],
    #
    'minLength': ['string'],
    'maxLength': ['string'],
    'pattern': ['string'],
    'format': ['string'],
    #
    'items': ['array'],
    'maxItems': ['array'],
    'minItems': ['array'],
    'uniqueItems': ['array'],
    'additionalItems': ['array'],
    #
    'properties': ['object'],
    'maxProperties': ['object'],
    'minProperties': ['object'],
    'additionalProperties': ['object'],
    'patternProperties': ['object'],
    'required': ['object'],
}
TYPE_NAMES = [
    'array', 'boolean', 'integer', 'null', 'number', 'object', 'string'
]
CLS_MAP = {
    'array': coreschema.Array,
    'boolean': coreschema.Boolean,
    'integer': coreschema.Integer,
    'null': coreschema.Null,
    'number': coreschema.Number,
    'object': coreschema.Object,
    'string': coreschema.String,
}


def camelcase_to_snakecase(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def load_jsonschema(data):
    type_kwargs = {type_name: {} for type_name in TYPE_NAMES}
    for keyword, value in data.items():
        # Load any nested schemas
        if keyword == 'items' and isinstance(value, dict):
            value = load_jsonschema(value)
        elif keyword == 'items' and isinstance(value, list):
            value = [load_jsonschema(item) for item in value]
        elif keyword == 'additionalItems' and isinstance(value, dict):
            value = load_jsonschema(value)
        elif keyword == 'properties' and isinstance(value, dict):
            value = {key: load_jsonschema(item) for key, item in value.items()}
        elif keyword == 'additionalProperties' and isinstance(value, dict):
            value = load_jsonschema(value)
        elif keyword == 'patternProperties' and isinstance(value, dict):
            value = {key: load_jsonschema(item) for key, item in value.items()}

        for type_name in KEYWORD_TO_TYPE.get(keyword, []):
            argument_name = camelcase_to_snakecase(keyword)
            type_kwargs[type_name][argument_name] = value

    if 'type' in data:
        valid_types = data.get('type')
        if isinstance(valid_types, text_types):
            # A string 'type' value is treated as a list with a single element.
            valid_types = [valid_types]
        for type_name in list(type_kwargs.keys()):
            if type_name not in valid_types:
                type_kwargs.pop(type_name)

    if 'integer' in type_kwargs and 'number' in type_kwargs:
        type_kwargs.pop('integer')

    schemas = []
    for type_name, kwargs in type_kwargs.items():
        cls = CLS_MAP[type_name]
        schemas.append(cls(**kwargs))

    if len(schemas) == 1:
        schema = schemas[0]
    schema = coreschema.Union(schemas)

    if 'enum' in data:
        # Restrict enum values by any existing type constraints,
        # and then use an Enum type.
        enum_values = [
            value for value in data['enum']
            if schema.validate(value) == []
        ]
        return coreschema.Enum(enum_values)

    return schema
