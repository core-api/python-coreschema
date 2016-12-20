from collections import namedtuple
from coreschema.formats import validate_format
import re


Error = namedtuple('Error', ['text', 'index'])


def push_index(errors, key):
    return [
        Error(error.text, [key] + error.index)
        for error in errors
    ]


text_types = (str, unicode)


def is_numeric_instance(value, types):
    """
    Python's booleans subclass int, so we need to explicitly disallow them
    when we're checking for numeric types that include int.
    Eg. isinstance(value, int) or isinstance(value, (float, int))
    """
    if isinstance(value, bool):
        return False
    return isinstance(value, types)


class Schema(object):
    errors = {}

    def make_error(self, code):
        error_string = self.errors[code]
        params = self.__dict__
        return Error(error_string.format(**params), [])


# TODO: enum, null (as keyword, as type), composites
# TODO: remaining formats
# Rename (core schema?)

# TODO: File
# TODO: strict, coerce float etc...

# TODO: decimals
# TODO: literal failure with single enum value
# TODO: override errors


class Object(Schema):
    errors = {
        'type': 'Must be an object.',
        'invalid_key': 'Object keys must be strings.',
        'empty': 'Must not be empty.',
        'required': 'This field is required.',
        'max_properties': 'Must have no more than {max_properties} properties.',
        'min_properties': 'Must have at least {min_properties} properties.',
        'invalid_property': 'Invalid property.'
    }

    def __init__(self, properties=None, required=None, max_properties=None, min_properties=None, pattern_properties=None, additional_properties=True):
        if isinstance(additional_properties, bool):
            # Handle `additional_properties` set to a boolean.
            self.additional_properties_schema = Anything()
        else:
            # Handle `additional_properties` set to a schema.
            self.additional_properties_schema = additional_properties
            additional_properties = True

        self.properties = properties
        self.required = required
        self.max_properties = max_properties
        self.min_properties = min_properties
        self.pattern_properties = pattern_properties
        self.additional_properties = additional_properties

        # Compile pattern regexes.
        self.pattern_properties_regex = None
        if pattern_properties is not None:
            self.pattern_properties_regex = {
                re.compile(key): value
                for key, value
                in pattern_properties.items()
            }

        # TODO: dependancies

    def validate(self, value):
        if not isinstance(value, dict):
            return [self.make_error('type')]

        errors = []
        if any(not isinstance(key, text_types) for key in value.keys()):
            errors += [self.make_error('invalid_key')]
        if self.required is not None:
            for key in self.required:
                if key not in value:
                    error_items = [self.make_error('required')]
                    errors += push_index(error_items, key)
        if self.min_properties is not None:
            if len(value) < self.min_properties:
                if self.min_properties == 1:
                    errors += [self.make_error('empty')]
                else:
                    errors += [self.make_error('min_properties')]
        if self.max_properties is not None:
            if len(value) > self.max_properties:
                errors += [self.make_error('max_properties')]

        # Properties
        remaining_keys = set(value.keys())
        if self.properties is not None:
            remaining_keys -= set(self.properties.keys())
            for key, property_item in self.properties.items():
                if key not in value:
                    continue
                error_items = property_item.validate(value[key])
                errors += push_index(error_items, key)

        # Pattern properties
        if self.pattern_properties is not None:
            for pattern, schema in self.pattern_properties_regex.items():
                for key in list(remaining_keys):
                    if re.search(pattern, key):
                        error_items = schema.validate(value[key])
                        errors += push_index(error_items, key)
                        remaining_keys.remove(key)

        # Additional properties
        if self.additional_properties:
            for key in remaining_keys:
                error_items = self.additional_properties_schema.validate(value[key])
                errors += push_index(error_items, key)
        else:
            for key in remaining_keys:
                error_items = [self.make_error('invalid_property')]
                errors += push_index(error_items, key)

        return errors


class Array(Schema):
    errors = {
        'type': 'Must be an array.',
        'empty': 'Must not be empty.',
        'max_items': 'Must have no more than {max_items} items.',
        'min_items': 'Must have at least {min_items} items.',
        'unique': 'Must not contain duplicate items.'
    }

    def __init__(self, items=None, max_items=None, min_items=None, unique_items=None):
        if items is None:
            items = Anything()

        self.items = items  # TODO: schema or list
        self.max_items = max_items
        self.min_items = min_items
        self.unique_items = unique_items
        # additional_items (TODO: boolean or schema)

    def validate(self, value):
        if not isinstance(value, list):
            return [self.make_error('type')]

        errors = []
        if self.items is not None:
            for idx, item in enumerate(value):
                error_items = self.items.validate(item)
                errors += push_index(error_items, idx)
        if self.min_items is not None:
            if len(value) < self.min_items:
                if self.min_items == 1:
                    errors += [self.make_error('empty')]
                else:
                    errors += [self.make_error('min_items')]
        if self.max_items is not None:
            if len(value) > self.max_items:
                errors += [self.make_error('max_items')]
        if self.unique_items is not None:
            if len(value) != len(set(value)):  # TODO: _utils.uniq
                errors += [self.make_error('unique')]

        return errors


class Number(Schema):
    number_type = (float, int)
    errors = {
        'type': 'Must be a number.',
        'minimum': 'Must be greater than or equal to {minimum}.',
        'exclusive_minimum': 'Must be greater than {minimum}.',
        'maximum': 'Must be less than or equal to {maximum}.',
        'exclusive_maximum': 'Must be less than {maximum}.',
        'multiple_of': 'Must be a multiple of {multiple_of}.',
    }

    def __init__(self, minimum=None, maximum=None, exclusive_minimum=False, exclusive_maximum=False, multiple_of=None):
        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of

    def validate(self, value):
        if not is_numeric_instance(value, self.number_type):
            return [self.make_error('type')]

        errors = []
        if self.minimum is not None:
            if self.exclusive_minimum:
                if value <= self.minimum:
                    errors += [self.make_error('exclusive_minimum')]
            else:
                if value < self.minimum:
                    errors += [self.make_error('minimum')]
        if self.maximum is not None:
            if self.exclusive_maximum:
                if value >= self.maximum:
                    errors += [self.make_error('exclusive_maximum')]
            else:
                if value > self.maximum:
                    errors += [self.make_error('maximum')]
        if self.multiple_of is not None:
            if isinstance(self.multiple_of, float):
                failed = not (float(value) / self.multiple_of).is_integer()
            else:
                failed = value % self.multiple_of
            if failed:
                errors += [self.make_error('multiple_of')]
        return errors


class Integer(Number):
    number_type = int
    errors = {
        'type': 'Must be an integer.',
        'minimum': 'Must be greater than or equal to {minimum}.',
        'exclusive_minimum': 'Must be greater than {minimum}.',
        'maximum': 'Must be less than or equal to {maximum}.',
        'exclusive_maximum': 'Must be less than {maximum}.',
        'multiple_of': 'Must be a multiple of {multiple_of}.',
    }


class String(Schema):
    errors = {
        'type': 'Must be a string.',
        'blank': 'Must not be blank.',
        'max_length': 'Must have no more than {max_length} characters.',
        'min_length': 'Must have at least {min_length} characters.',
        'pattern': 'Must match the pattern /{pattern}/.',
        'format': 'Must be a valid {format}.',
        'enum': 'Must be one of {enum}.',
    }

    def __init__(self, max_length=None, min_length=None, pattern=None, format=None, enum=None):
        self.max_length = max_length
        self.min_length = min_length
        self.pattern = pattern
        self.format = format
        self.enum = enum

        self.pattern_regex = None
        if self.pattern is not None:
            self.pattern_regex = re.compile(pattern)

    def validate(self, value):
        if not isinstance(value, text_types):
            return [self.make_error('type')]

        errors = []
        if self.min_length is not None:
            if len(value) < self.min_length:
                if self.min_length == 1:
                    errors += [self.make_error('blank')]
                else:
                    errors += [self.make_error('min_length')]
        if self.max_length is not None:
            if len(value) > self.max_length:
                errors += [self.make_error('max_length')]
        if self.pattern is not None:
            if not re.search(self.pattern_regex, value):
                errors += [self.make_error('pattern')]
        if self.format is not None:
            if not validate_format(value, self.format):
                errors += [self.make_error('format')]
        if self.enum is not None:
            if value not in self.enum:
                errors += [self.make_error('enum')]
        return errors


class Boolean(Schema):
    errors = {
        'type': 'Must be a boolean.'
    }

    def validate(self, value):
        if not isinstance(value, bool):
            return [self.make_error('type')]

        return []


class Anything(Schema):
    errors = {
        'type': 'Must be a valid primitive type.'
    }
    types = text_types + (dict, list, int, float, bool, type(None))

    def validate(self, value):
        if not isinstance(value, self.types):
            return [self.make_error('type')]

        errors = []
        if isinstance(value, list):
            schema = Array()
            errors += schema.validate(value)
        elif isinstance(value, dict):
            schema = Object()
            errors += schema.validate(value)
        return errors
