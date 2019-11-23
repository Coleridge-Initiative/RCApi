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
        search_term = "deal or no deal?"
        pub_list = schol.dimensions.full_text_search(search_term)

        print("\ntime: {:.3f} ms - {}".format(schol.dimensions.elapsed_time, schol.dimensions.name))

        for pub in pub_list:
            if pub["doi"] == "10.1016/j.appet.2019.104481":
                self.assertTrue(pub["journal"]["title"] == "Appetite")
                return

        self.assertTrue("DOI not found" == "")


    def test_repec_handle_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Estimating the 'True' Cost of Job Loss: Evidence Using Matched Data from California 1991-2000"

        handle = schol.repec.get_handle(title)

        print("\ntime: {:.3f} ms - {}".format(schol.repec.elapsed_time, schol.repec.name))
        self.assertTrue(handle == "RePEc:cen:wpaper:09-14")


if __name__ == "__main__":
    unittest.main()
