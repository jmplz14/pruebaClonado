# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

import transaction
import unittest2 as unittest
from dnota.lims.config import PRODUCT_NAME
from dnota.lims.config import PROFILE_ID
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import zope


class SimpleTestLayer(PloneSandboxLayer):
    """Setup Plone with installed Add-on only
    """
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):  # noqa CamelCase
        super(SimpleTestLayer, self).setUpZope(app, configurationContext)

        # Load ZCML
        import archetypes.schemaextender
        import bika.lims
        import senaite.core
        import senaite.lims
        import dnota.lims

        self.loadZCML(package=archetypes.schemaextender)
        self.loadZCML(package=bika.lims)
        self.loadZCML(package=senaite.core)
        self.loadZCML(package=senaite.lims)
        self.loadZCML(package=dnota.lims)

        # Install product and call its initialize() function
        zope.installProduct(app, "bika.lims")
        zope.installProduct(app, "senaite.core")
        zope.installProduct(app, "senaite.lims")
        zope.installProduct(app, PRODUCT_NAME)

    def setUpPloneSite(self, portal):  # noqa CamelCase
        super(SimpleTestLayer, self).setUpPloneSite(portal)
        applyProfile(portal, PROFILE_ID)
        transaction.commit()


###
# Use for simple tests (w/o contents)
###
SIMPLE_FIXTURE = SimpleTestLayer()
SIMPLE_TESTING = FunctionalTesting(
    bases=(SIMPLE_FIXTURE, ),
    name="{}:SimpleTesting".format(PRODUCT_NAME)
)


class SimpleTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(SimpleTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Manager"])
