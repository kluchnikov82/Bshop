"""Vase validators"""

from django.core.validators import _lazy_re_compile, RegexValidator


slug_re = _lazy_re_compile(r'^[-a-z0-9]+\Z')

validate_slug = RegexValidator(
    slug_re,
    'Разрешены только буквы английского алфавита в нижнем регистре, цифры, дефисы',
    'invalid'
)
