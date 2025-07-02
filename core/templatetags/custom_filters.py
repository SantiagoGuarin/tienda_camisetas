# core/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def average(queryset, field_name):
    values = [getattr(obj, field_name, 0) for obj in queryset if getattr(obj, field_name, None) is not None]
    return sum(values) / len(values) if values else 0

@register.filter
def estrellas(promedio):
    try:
        promedio = float(promedio)
    except:
        return "☆☆☆☆☆"

    llenas = int(promedio)
    vacías = 5 - llenas
    return "⭐" * llenas + "☆" * vacías