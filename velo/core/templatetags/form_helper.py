from django import template, forms
register = template.Library()


@register.filter
def add_class(field, css):
   return field.as_widget(attrs={"class": css})


@register.filter
def add_extra_classes(field, extra_classes=None):
    classes = field.field.widget.attrs.get('class', '')
    if hasattr(classes, 'split'):
        classes = classes.split()
    classes = set(classes or [])
    classes.add(field.css_classes())
    if extra_classes:
        classes.add(extra_classes)
    return field.as_widget(attrs={"class": ' '.join(classes)})


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_password(field):
    return isinstance(field.field.widget, forms.PasswordInput)


@register.filter
def is_radioselect(field):
    return isinstance(field.field.widget, forms.RadioSelect)


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_checkboxselectmultiple(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.ClearableFileInput)

