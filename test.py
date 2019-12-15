#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import unittest

   
class TestOpenAPIs (unittest.TestCase):

    def test_europepmc_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Zebrafish models: Gaining insight into purinergic signaling and neurological disorders"
        meta = schol.europepmc.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.europepmc.elapsed_time, schol.europepmc.name))
        self.assertTrue(repr(meta) == "OrderedDict([('doi', '10.1016/j.pnpbp.2019.109770'), ('pmcid', None), ('journal', 'Prog Neuropsychopharmacol Biol Psychiatry'), ('authors', ['Nabinger DD', 'Altenhofen S', 'Bonan CD.'])])")


    def test_openaire_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        meta = schol.openaire.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.openaire.elapsed_time, schol.openaire.name))
        self.assertTrue(repr(meta) == "OrderedDict([('url', 'https://europepmc.org/articles/PMC5574185/'), ('authors', ['Taillie, Lindsey Smith', 'Ng, Shu Wen', 'Xue, Ya', 'Harding, Matthew']), ('open', True)])")


    def test_crossref_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1503/cmaj.170880"

        meta = schol.crossref.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(schol.crossref.elapsed_time, schol.crossref.name))
        self.assertTrue(meta["URL"] == "http://dx.doi.org/10.1503/cmaj.170880")


    def test_crossref_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit"

        meta = schol.crossref.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.crossref.elapsed_time, schol.crossref.name))
        self.assertTrue(meta["URL"] == "http://dx.doi.org/10.1177/0042098017740285")


    def test_crossref_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "NHANES"

        search_results = schol.crossref.full_text_search(search_term)

        print("\ntime: {:.3f} ms - {}".format(schol.crossref.elapsed_time, schol.crossref.name))
        self.assertTrue(search_results["total-results"] >= 884000)


    def test_pubmed_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Climate-change-driven accelerated sea-level rise detected in the altimeter era"

        meta = schol.pubmed.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(schol.pubmed.elapsed_time, schol.pubmed.name))
        self.assertTrue(meta["MedlineCitation"]["PMID"]["#text"] == "29440401")


    def test_semantic_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"

        meta = schol.semantic.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(schol.semantic.elapsed_time, schol.semantic.name))
        self.assertTrue(meta["url"] == "https://www.semanticscholar.org/paper/690195fe2ab0fa093204a050ceb2f9fd1d1b2907")


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


    def test_unpaywall_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"

        meta = schol.unpaywall.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(schol.unpaywall.elapsed_time, schol.unpaywall.name))
        self.assertTrue(meta["doi_url"] == "https://doi.org/10.1016/j.appet.2017.07.006")


    def test_dissemin_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"

        meta = schol.dissemin.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(schol.dissemin.elapsed_time, schol.dissemin.name))
        self.assertTrue(meta["paper"]["date"] == "2017-10-01")


    def test_repec_handle_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Estimating the 'True' Cost of Job Loss: Evidence Using Matched Data from California 1991-2000"

        handle = schol.repec.get_handle(title)

        print("\ntime: {:.3f} ms - {}".format(schol.repec.elapsed_time, schol.repec.name))
        self.assertTrue(handle == "RePEc:cen:wpaper:09-14")


if __name__ == "__main__":
    unittest.main()
