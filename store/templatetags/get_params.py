from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def reget_params(context, **kwargs):
    """
    Returns a string of the current GET parameters with the specified
    parameters added.
    """
    request = context['request']
    params = request.GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    return params.urlencode()

@register.simple_tag(takes_context=True)
def remove_params(context, **kwargs):
    """
    Returns a string of the current GET parameters with the specified
    parameters removed.
    """
    request = context['request']
    params = request.GET.copy()
    for k, v in kwargs.items():
        params.pop(k, None)
    return params.urlencode()