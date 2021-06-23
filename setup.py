# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

from setuptools import setup, find_packages

version = "1.0.0"

setup(
    name="dnota.lims",
    version=version,
    description="SENAITE extension profile for DNOTA",
    long_description=open("README.md").read(),
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2",
    ],
    keywords="",
    author="NARALABS",
    author_email="info@naralabs.com",
    url="https://github.com/naralabs/dnota.lims",
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    namespace_packages=["dnota"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "senaite.lims",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "unittest2",
        ]
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
