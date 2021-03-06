# from https://stackoverflow.com/questions/1052531/get-user-group-in-a-template
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

# Stdlib imports

# Core Django imports
from django import template

# Third-party app imports

# Realative imports of the 'app-name' package


register = template.Library()

@register.filter(name='times')
def times(number):
    return range(number)

@register.filter
def modulo(num, val):
    return num % val

@register.filter('has_group')
def has_group(user, group_name):
    """
    Verifica se este usuário pertence a um grupo
    """
    groups = user.groups.all().values_list('name', flat=True)
    return True if group_name in groups else False