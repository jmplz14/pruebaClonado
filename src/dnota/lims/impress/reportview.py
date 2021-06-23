# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

from senaite.impress.analysisrequest.reportview import MultiReportView


class DNotaMultiReportView(MultiReportView):
    """DNota-specific controller view for multiple results reports
    """

    def long_date(self, date):
        """Returns the localized date in long format
        """
        return self.to_localized_time(date, long_format=1)

    def short_date(self, date):
        """Returns the localized date in short format
        """
        return self.to_localized_time(date, long_format=0)
