#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import time
import unittest

   
class TestCallAPIs (unittest.TestCase):

    def test_europepmc_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        meta = schol.europepmc.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.europepmc.elapsed_time, schol.europepmc.name))
        self.assertTrue(repr(meta) == "OrderedDict([('doi', '10.1016/j.appet.2017.07.006'), ('pmcid', 'PMC5574185'), ('journal', 'Appetite'), ('authors', ['Taillie LS', 'Ng SW', 'Xue Y', 'Harding M.']), ('pdf', 'http://europepmc.org/articles/PMC5574185?pdf=render')])")


    def test_openaire_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        meta = schol.openaire.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.openaire.elapsed_time, schol.openaire.name))
        self.assertTrue(repr(meta) == "OrderedDict([('url', 'https://europepmc.org/articles/PMC5574185/'), ('authors', ['Taillie, Lindsey Smith', 'Ng, Shu Wen', 'Xue, Ya', 'Harding, Matthew']), ('open', True)])")


    def test_repec_handle_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Estimating the 'True' Cost of Job Loss: Evidence Using Matched Data from California 1991-2000"

        t0 = time.time()
        handle = schol.repec_get_handle(title)
        t1 = time.time()

        print("\ntime: {:.3f} ms - RePEc".format((t1 - t0) * 1000.0))
        self.assertTrue(handle == "RePEc:cen:wpaper:09-14")


    def test_semantic_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"

        t0 = time.time()
        meta = schol.semantic_publication_lookup(doi)
        t1 = time.time()

        print("\ntime: {:.3f} ms - Semantic Scholar".format((t1 - t0) * 1000.0))
        self.assertTrue(meta["url"] == "https://www.semanticscholar.org/paper/690195fe2ab0fa093204a050ceb2f9fd1d1b2907")


    def test_unpaywall_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"
        email = "info@derwen.ai"

        t0 = time.time()
        meta = schol.unpaywall_publication_lookup(doi, email)
        t1 = time.time()

        print("\ntime: {:.3f} ms - Unpaywall".format((t1 - t0) * 1000.0))
        self.assertTrue(meta["doi_url"] == "https://doi.org/10.1016/j.appet.2017.07.006")


    def test_dissemin_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"

        t0 = time.time()
        meta = schol.dissemin_publication_lookup(doi)
        t1 = time.time()

        print("\ntime: {:.3f} ms - dissemin".format((t1 - t0) * 1000.0))
        self.assertTrue(meta["paper"]["date"] == "2017-10-01")


if __name__ == "__main__":
    unittest.main()
