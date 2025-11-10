from django import template

register = template.Library()

@register.filter(name='mul')
def multiply(value, arg):
    try:
        return value * arg
    except:
        return value
