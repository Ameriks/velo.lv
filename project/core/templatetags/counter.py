from django import template

from django.conf import settings
import re

from django import template
from django.utils.encoding import force_unicode

TEMPLATEADDONS_COUNTERS_VARIABLE = getattr(settings, 'TEMPLATEADDONS_COUNTER_GLOBAL_VARIABLE', '_templateaddons_counters')

register = template.Library()

def parse_tag_argument(argument, context):
    """Parses a template tag argument within given context.

    Consider the tag:
    {% my_tag name='Toto' surname="Tata" age=32 size=1.70 person=object.get_person %}

    The values used above are interpreted as:
    - 'Toto' and "Tata" are converted to their string value (without quotes),
    respectively 'Toto' and 'Tata'
    - 32 is converted to an integer
    - 1.70 is converted to a float
    - object.get_person is interpreted as a variable and parsed within the context
    """
    if isinstance(argument, (str, unicode)) and argument:
        if argument[0] == argument[-1] and argument[0] in ('"', "'"):
            argument = argument[1:-1]
        else:
            m = re.match(r'(?P<int>\d+)(\.(?P<decimal>\d+))?', argument)
            if m is not None:
                if m.group('decimal'):
                    argument = float(argument)
                else:
                    argument = int(argument)
            else:
                argument = template.Variable(argument).resolve(context)
    return argument


split_re = re.compile('(?P<left>[\w-]+=)?(?P<right>"(?:[^"\\\\]*(?:\\\\.[^"\\\\]*)*)"|\'(?:[^\'\\\\]*(?:\\\\.[^\'\\\\]*)*)\'|[^\\s]+)')
def split_arguments(str):
    """
    Inspired by django.template.Token.split_contents(), except that arguments
    can be named.
    """
    str = force_unicode(str)
    str = str.split(u' ', 1)
    if not len(str) > 1:
        return []
    str = str[1]
    arguments = []
    for match in split_re.finditer(str):
        left = match.group('left') or u''
        right = match.group('right') or u''
        if right[0] == '"' and right[-1] == '"':
            right = '"' + right[1:-1].replace('\\"', '"').replace('\\\\', '\\') + '"'
        elif right[0] == "'" and right[-1] == "'":
            right = "'" + right[1:-1].replace("\\'", "'").replace("\\\\", "\\") + "'"
        else:
            pass
        arguments.append(left + right)
    return arguments


def decode_tag_argument(argument):
    """Extracts argument name and value from the given string"""
    match = re.match(r'((?P<name>[\w-]+)=)?(?P<value>.+)', argument)
    if match is None:
        raise template.TemplateSyntaxError, "invalid tag argument syntax '%s'" % argument
    else:
        return {'name': str(match.group('name')), 'value':match.group('value')}


def decode_tag_arguments(token, default_arguments={}):
    """Returns a dictionnary of arguments that can be found in the given token.

    This can be useful to code template tags like this:
    {% my_tag name='Toto' surname="Tata" age=32 size=1.70 person=object.get_person %}
    In this syntax, arguments order is not important.

    You can provide default argument values with the parameter default_arguments.
    """
    arguments = {}
    args = split_arguments(token.contents)

    for (arg_name, arg_value) in default_arguments.iteritems():
        arguments[arg_name] = arg_value

    for arg in args:
        argument = decode_tag_argument(arg)
        arguments[argument['name']] = argument['value']

    return arguments

class Counter:
    def __init__(self, start=0, step=1, ascending=True):
        self.value = start
        self.start = start
        self.step = step
        self.ascending = ascending


class CounterNode(template.Node):
    def __init__(self, name='"default"', start=0, step=1, ascending=True,
                 silent=False, assign=False):
        self.name = name
        self.start = start
        self.step = step
        self.ascending = ascending
        self.silent = silent
        self.assign = assign

    def render(self, context):
        # global context initialization
        if not context.has_key(TEMPLATEADDONS_COUNTERS_VARIABLE):
            context[TEMPLATEADDONS_COUNTERS_VARIABLE] = {}
        counters = context[TEMPLATEADDONS_COUNTERS_VARIABLE]

        name = parse_tag_argument(self.name, context)
        silent = parse_tag_argument(self.silent, context)
        assign = parse_tag_argument(self.assign, context)

        if not counters.has_key(name):
            start = parse_tag_argument(self.start, context)
            step = parse_tag_argument(self.step, context)
            ascending = parse_tag_argument(self.ascending, context)
            counters[name] = Counter(start, step, ascending)
        else:
            if counters[name].ascending:
                counters[name].value += counters[name].step
            else:
                counters[name].value -= counters[name].step

        context[TEMPLATEADDONS_COUNTERS_VARIABLE] = counters

        if assign:
            context[assign] = counters[name].value

        if self.silent:
            return u''
        else:
            return u'%d' % counters[name].value


def counter(parser, token):
    default_arguments = {}
    default_arguments['name'] = '"default"'
    default_arguments['start'] = 0
    default_arguments['step'] = 1
    default_arguments['ascending'] = True
    default_arguments['silent'] = False
    default_arguments['assign'] = '""'

    arguments = decode_tag_arguments(token, default_arguments)

    return CounterNode(**arguments)

register.tag('counter', counter)