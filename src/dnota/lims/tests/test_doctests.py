# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

import doctest
from os.path import join

import unittest2 as unittest
from dnota.lims.config import PRODUCT_NAME
from pkg_resources import resource_listdir
from Testing import ZopeTestCase as ztc

from .base import SimpleTestCase

# Option flags for doctests
FLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF


def get_doctest_files():
    """Returns a list with the doctest files
    """
    files = resource_listdir(PRODUCT_NAME, "tests/doctests")
    files = filter(lambda file_name: file_name.endswith(".rst"), files)
    return map(lambda file_name: join("doctests", file_name), files)


def test_suite():
    suite = unittest.TestSuite()
    for doctest_file in get_doctest_files():
        suite.addTests([
            ztc.ZopeDocFileSuite(
                doctest_file,
                test_class=SimpleTestCase,
                optionflags=FLAGS
            )
        ])
    return suite
