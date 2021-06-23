# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

import logging

from bika.lims.api import get_request
from dnota.lims.config import PRODUCT_NAME
from dnota.lims.interfaces import IDNOTALimsLayer
from zope.i18nmessageid import MessageFactory

logger = logging.getLogger(PRODUCT_NAME)
messageFactory = MessageFactory(PRODUCT_NAME)


def is_installed():
    """Returns whether the product is installed or not
    """
    request = get_request()
    return IDNOTALimsLayer.providedBy(request)


def check_installed(default_return):
    """Decorator to prevent the function to be called if product not installed
    :param default_return: value to return if not installed
    """
    def is_installed_decorator(func):
        def wrapper(*args, **kwargs):
            if not is_installed():
                return default_return
            return func(*args, **kwargs)
        return wrapper
    return is_installed_decorator


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing DNOTA LIMS Customization package ***")
