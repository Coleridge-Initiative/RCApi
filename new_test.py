#!/usr/bin/env python
# encoding: utf-8

import unittest
import rcapi

   
class TestCallAPIs (unittest.TestCase):

    def test_europepmc_title_search (self):
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."

        meta = rcapi.europepmc_title_search(title)
        self.assertTrue(repr(meta) == "OrderedDict([('doi', '10.1016/j.appet.2017.07.006'), ('pmcid', 'PMC5574185'), ('journal', 'Appetite'), ('authors', ['Taillie LS', 'Ng SW', 'Xue Y', 'Harding M.']), ('pdf', 'http://europepmc.org/articles/PMC5574185?pdf=render')])")


if __name__ == "__main__":
    unittest.main()
