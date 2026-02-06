from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_isdigit(value):
    if not value.isdigit():
        raise ValidationError(
            _("%(value)s is not a number"),
            params={"value": value},
        )


def validate_inn_length(value):
    if len(value) < 9:
        raise ValidationError(
            _("%(value)s length of a is less than 9"),
            params={"value": value},
        )


def validate_pinfl_length(value):
    if len(value) < 14:
        raise ValidationError(
            _("%(value)s length of a is less than 14"),
            params={"value": value},
        )


def validate_pass_seria_length(value):
    if len(value) < 2:
        raise ValidationError(
            _("%(value)s length of a is less than 2"),
            params={"value": value},
        )


def validate_pass_number_length(value):
    if len(value) < 7:
        raise ValidationError(
            _("%(value)s length of a is less than 7"),
            params={"value": value},
        )


def validate_phone_number_length(value):
    if len(value) < 12:
        raise ValidationError(
            _("%(value)s length of a is less than 12"),
            params={"value": value},
        )