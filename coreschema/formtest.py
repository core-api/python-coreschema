from coreschema import Object, Array, String, Integer, Number, Boolean, Enum
from coreschema.forms import determine_html_template, get_attrs, get_textarea_value
import jinja2

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('coreschema', 'templates'))


example = Object(
    properties={
        #'string': String(),
        'number': Number(),
        'integer': Integer(),
        'object': Object(),
        'boolean': Boolean(),
        'enum': Enum(['cat', 'dog', 'rabbit']),
        'multi_select': Array(Enum(['cat', 'dog', 'rabbit']), unique_items=True),
        'array': Array()
    }
)


template = env.get_template('base.html')
print template.render({
    'parent': example,
    'determine_html_template': determine_html_template,
    'get_textarea_value': get_textarea_value,
    'get_attrs': get_attrs
})
