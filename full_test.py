#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
from test import TestOpenAPIs
import unittest

   
class TestAllAPIs (TestOpenAPIs):

    def test_ssrn_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.ssrn

        doi = "10.2139/ssrn.2898991"
        expectaed = "OrderedDict([('doi', '10.2139/ssrn.2898991'), ('title', 'Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit'), ('keywords', ['place-based policies', 'retail food', 'tax incentives', 'community health', 'regression discontinuity']), ('authors', ['Freedman, Matthew', 'Kuhns, Annemarie'])])"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            source.report_perf(timing)
            self.assertTrue(repr(meta) == expected)


    def test_ssrn_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.ssrn

        title = "Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit"
        expected = "OrderedDict([('doi', '10.2139/ssrn.2898991'), ('title', 'Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit'), ('keywords', ['place-based policies', 'retail food', 'tax incentives', 'community health', 'regression discontinuity']), ('authors', ['Freedman, Matthew', 'Kuhns, Annemarie'])])"

        if source.has_credentials():
            meta, timing, message = source.title_search(title)
            source.report_perf(timing)
            self.assertTrue(repr(meta) == expected)


if __name__ == "__main__":
    unittest.main()
