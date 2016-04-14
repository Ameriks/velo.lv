# -*- coding: utf-8 -*-
"""
Templatetag that fixes problems with request.GET manipulation in templates.
Example usage:

Add static var with static value to get:
* {% urlget 'var'='val' %}

Add dynamic val (from template vars) to static variable:
* {% urlget 'var'=val %}

Using dynamic variable names works similiar - adding dynamic varialbe
(from template vars):
* {% urlget var='val' %}

Clearing variable from GET string:
* {% urlget 'var'='' %}

Retrieving GET string:
* {% urlget %}
"""


from django.template import Library
from django import template

register = Library()


def do_urlget(parser, token):
    u"""Prepare data for urlget"""
    tmp = token.split_contents()
    if len(tmp) > 1:
        _tag_name, data = tmp
    else:
        _tag_name = tmp
        data = None
    return URLGetNode(data)


class URLGetNode(template.Node):
    u"""urlget renderer class"""

    def __init__(self, data):
        u"""Setup parameters"""
        super(URLGetNode, self).__init__()
        self.data = data

    def get_value(self, val, context):
        u"""
        Read value of variable from template context or return variable name
        as value
        """
        if val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        else:
            val = template.Variable(val).resolve(context)
        return str(val)

    def render(self, context):
        """Render new GET string"""
        request = context['request']
        get_data = request.GET.copy()

        tag_params = {}
        if self.data:
            param_list = self.data.split('&')

            # Setup tag parameters
            for item in param_list:
                param_key, param_val = item.split('=')
                key = self.get_value(param_key, context)
                val = self.get_value(param_val, context)
                tag_params[key] = val

            for key, val in tag_params.items():
                if key in get_data:
                    del get_data[key]
                    if val:
                        get_data.update({key: val})
                else:
                    get_data.update({key: val})

            output = get_data.urlencode()
            if output:
                return u"?%s" % output
            else:
                return ""

register.tag('urlget', do_urlget)
