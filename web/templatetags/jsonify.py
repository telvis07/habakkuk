from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def jsonify(list):
    return mark_safe(json.dumps(list))
