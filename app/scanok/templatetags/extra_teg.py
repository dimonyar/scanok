import datetime
from django import template


register = template.Library()


@register.filter
def tact_to_data(tact):
    return (datetime.datetime.min + datetime.timedelta(seconds=tact/10000000)).strftime("%d/%m/%Y %H:%M:%S")


@register.filter
def zfill(value, arg):
    return value.zfill(arg)
