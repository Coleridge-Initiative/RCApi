#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
from test import TestOpenAPIs
import unittest

   
class TestAllAPIs (TestOpenAPIs):

    def test_dimensions_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        meta = schol.dimensions.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.dimensions.elapsed_time, schol.dimensions.name))
        self.assertTrue(meta["doi"] == "10.1016/j.appet.2017.07.006")


    def test_dimensions_full_text_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "the French paradox"
        pub_list = schol.dimensions.full_text_search(search_term)

        print("\ntime: {:.3f} ms - {}".format(schol.dimensions.elapsed_time, schol.dimensions.name))

        for pub in pub_list:
            if pub["doi"] == "10.1016/j.foodchem.2019.125340":
                self.assertTrue(pub["journal"]["title"] == "Food Chemistry")
                return

        self.assertTrue("DOI not found" == "")


    def test_ssrn_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.2139/ssrn.2898991"

        meta = schol.ssrn.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(schol.ssrn.elapsed_time, schol.ssrn.name))
        self.assertTrue(repr(meta) == "OrderedDict([('doi', '10.2139/ssrn.2898991'), ('title', 'Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit'), ('keywords', ['place-based policies', 'retail food', 'tax incentives', 'community health', 'regression discontinuity']), ('authors', ['Freedman, Matthew', 'Kuhns, Annemarie'])])")


    def test_ssrn_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit"

        meta = schol.ssrn.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.ssrn.elapsed_time, schol.ssrn.name))
        self.assertTrue(repr(meta) == "OrderedDict([('doi', '10.2139/ssrn.2898991'), ('title', 'Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit'), ('keywords', ['place-based policies', 'retail food', 'tax incentives', 'community health', 'regression discontinuity']), ('authors', ['Freedman, Matthew', 'Kuhns, Annemarie'])])")


if __name__ == "__main__":
    unittest.main()
