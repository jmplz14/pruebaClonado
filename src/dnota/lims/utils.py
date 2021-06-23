# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

from dnota.lims import messageFactory as _

from bika.lims.utils import t as _t
from bika.lims.utils import to_utf8


def set_field_value(instance, field_name, value):
    field = instance.getField(field_name)
    if hasattr(field, "mutator") and field.mutator:
        mutator = getattr(instance, field.mutator)
        if mutator:
            mutator(value)
            return

    # Apply the value directly to the schema's field
    field.set(instance, value)


def get_field_value(instance, field_name):
    """Returns the value of a Schema field
    """
    return instance.getField(field_name).get(instance)


def translate(i18n_message, mapping=None):
    """Translates a message and handles mapping
    """
    return to_utf8(_t(_(i18n_message, mapping=mapping)))
