from coreschema import Object, Array, String, Anything, Boolean


media_type_pattern = '^[^/]+/[^/]'


# TODO Reference

SecurityScheme = Anything()  # TODO
XMLObject = Anything()  # TODO
Header = Anything()  # TODO
Schema = Anything()  # TODO
Items = Anything()  # TODO

Definitions = Object(additional_properties=Schema)

ExternalDocumentation = Object(
    properties={
        'description': String(),
        'url': String(format='uri')
    },
    pattern_properties={
        '^x-': Anything()
    },
    required=['url'],
    additional_properties=False
)


Tag = Object(
    properties={
        'name': String(),
        'description': String(),
        'externalDocs': ExternalDocumentation
    },
    pattern_properties={
        '^x-': Anything()
    },
    required=['name'],
    additional_properties=False
)

Examples = Object(pattern_properties={
    media_type_pattern: Anything()
})

Headers = Object(additional_properties=Header)

Response = Object(
    properties={
        'description': String(),
        'schema': Schema,
        'headers': Headers,
        'examples': Examples
    },
    pattern_properties={
        '^x-': Anything()
    },
    required=['description'],
    additional_properties=False
)

Responses = Object(
    properties={
        'default': Response  # Allow ref
    },
    pattern_properties={
        '^[1-5][0-9][0-9]$': Response,  # Allow ref
        '^x-': Anything()
    },
    additional_properties=False
)

Parameter = Object(
    properties={
        'name': String(), # If 'in' is 'path' then must be segment in path template variable
        'in': String(enum=['query', 'header', 'path', 'formData', 'body']),
        'description': String(),
        'required': Boolean()  # If 'in' is 'path' then required and true.
    },
    additional_properties=True,  # TODO body -> schema, others -> ...
    required=['name', 'in']
)

Operation = Object(
    properties={
        'tags': Array(String(), unique_items=True),
        'summary': String(),  # SHOULD be < 120
        'description': String(),
        'externalDocs': ExternalDocumentation,
        'operationId': String(),  # MUST be unique
        'consumes': Array(String(pattern=media_type_pattern), unique_items=True),
        'produces': Array(String(pattern=media_type_pattern), unique_items=True),
        'parameters': Array(Parameter),   # Allow ref
        'responses': Responses,
        'schemes': Array(String(enum=['http', 'https', 'ws', 'wss']), unique_items=True),
        'deprecated': Boolean(),
        'security': Anything()  # TODO
    },
    pattern_properties={
        '^x-': Anything()
    },
    required=['responses'],
    additional_properties=False
)

PathItem = Object(
    properties={  # Allow ref
        'get': Operation,
        'put': Operation,
        'post': Operation,
        'delete': Operation,
        'options': Operation,
        'head': Operation,
        'patch': Operation,
        'parameters': Array(Parameter)  # Allow ref
    },
    pattern_properties={
        '^x-': Anything()
    },
    additional_properties=False
)

Paths = Object(
    pattern_properties={
        '^/': PathItem,
        '^x-': Anything()
    },
    additional_properties=False
)

License = Object(
    properties={
        'name': String(),
        'url': String(format='uri')
    },
    pattern_properties={'^x-': Anything()},
    required=['name'],
    additional_properties=False
)

Contact = Object(
    properties={
        'name': String(),
        'url': String(format='uri'),
        'email': String(format='email')
    },
    pattern_properties={'^x-': Anything()},
    additional_properties=False
)

Info = Object(
    properties={
        'title': String(),
        'description': String(),
        'termsOfService': String(),
        'contact': Contact,
        'license': License,
        'version': String()
    },
    pattern_properties={'^x-': Anything()},
    required=['title', 'version'],
    additional_properties=False
)

Swagger = Object(
    properties={
        'swagger': String(enum=['2.0']),
        'info': Info,
        'host': String(),
        'basePath': String(),
        'schemes': Array(String(enum=['http', 'https', 'ws', 'wss']), unique_items=True),
        'consumes': Array(String(pattern=media_type_pattern), unique_items=True),
        'produces': Array(String(pattern=media_type_pattern), unique_items=True),
        'paths': Paths,
        # Definition space...  (Used by refs)
        'definitions': Object(additional_properties=Schema),
        'parameters': Object(additional_properties=Parameter),
        'responses': Object(additional_properties=Responses),
        'securityDefinitions':  Object(additional_properties=SecurityScheme),
        # Security space... (Used by ...)
        'security': Array(Anything()),  # TODO
        # Tag space... (Used by operations)
        'tags': Array(Tag),  # names MUST be unique
        'externalDocs': ExternalDocumentation
    },
    pattern_properties={'^x-': Anything()},
    required=['swagger', 'info', 'paths'],
    additional_properties=False
)


# swagger = Swagger.parse({
#     'info': {
#         'title': doc.title,
#         'description': doc.description
#     },
#     'paths': paths
# })
# swagger.value


swagger = Swagger.parse(input_content)

title = swagger.get(['info', 'title'])
description = swagger.get(['info', 'description'], default='')
version = swagger.get(['info', 'version'])

default_schemes = swagger.get('schemes', default=[])
default_consumes = swagger.get('consumes', default=None)
default_produces = swagger.get('produces', default=None)
for path, path_item in swagger.walk_items('PathItem'):
    default_properties = path_item.get('properties', default=[])
    for method, operation in path_item.walk_items('Operation'):
        operation_id = operation.get('operationId')
        tags = operation.get('tags', default=[])
        schemes = operation.get(['schemes'], default=default_schemes)
        consumes = operation.get(['consumes'], default=default_consumes)
        produces = operation.get(['produces'], default=default_produces)
        properties = operation.get(['properties'], default=default_properties)


import os
import json
input_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petstore.json')
schema = json.loads(open(input_path, 'r').read())

print Swagger.validate(schema)
