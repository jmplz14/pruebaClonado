# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

from senaite.impress.interfaces import ISenaiteImpressLayer
from senaite.lims.interfaces import ISenaiteLIMS


class IDNOTALimsLayer(ISenaiteLIMS, ISenaiteImpressLayer):
    """Zope 3 browser Layer interface specific for this add-on
    This interface is referred in profiles/default/browserlayer.xml.
    All views and viewlets register against this layer will appear in the site
    only when the add-on installer has been run.
    """
