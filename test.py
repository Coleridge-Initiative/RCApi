#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import pprint
import unittest

   
class TestOpenAPIs (unittest.TestCase):

    def test_europepmc_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Zebrafish models: Gaining insight into purinergic signaling and neurological disorders"
        meta, timing, message = schol.europepmc.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.europepmc.name))
        self.assertTrue(repr(meta) == "OrderedDict([('doi', '10.1016/j.pnpbp.2019.109770'), ('journal', 'Prog Neuropsychopharmacol Biol Psychiatry'), ('authors', ['Nabinger DD', 'Altenhofen S', 'Bonan CD.'])])")


    def test_openaire_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        meta, timing, message = schol.openaire.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.openaire.name))
        self.assertTrue(repr(meta) == "OrderedDict([('url', 'https://europepmc.org/articles/PMC5574185/'), ('authors', ['Taillie, Lindsey Smith', 'Ng, Shu Wen', 'Xue, Ya', 'Harding, Matthew']), ('open', True)])")

    
    def test_openaire_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "NHANES"
        meta, timing, message = schol.openaire.full_text_search(search_term, limit=100)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.openaire.name))
        self.assertTrue(len(meta) >= 100)


    def test_crossref_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1503/cmaj.170880"
        meta, timing, message = schol.crossref.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.crossref.name))
        self.assertTrue(meta["title"][0] == "Relation between household food insecurity and breastfeeding in Canada")


    def test_crossref_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Relation between household food insecurity and breastfeeding in Canada"
        meta, timing, message = schol.crossref.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.crossref.name))
        self.assertTrue(meta["DOI"] == "10.1503/cmaj.170880")
        

    def test_crossref_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "NHANES"
        meta, timing, message = schol.crossref.full_text_search(search_term, limit=100)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.crossref.name))
        self.assertTrue(meta["total-results"] >= 100)


    def test_pubmed_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Climate-change-driven accelerated sea-level rise detected in the altimeter era"
        meta, timing, message = schol.pubmed.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.pubmed.name))
        self.assertTrue(meta["MedlineCitation"]["PMID"]["#text"] == "29440401")


    def test_pubmed_journal_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        issn = "1932-6203"
        meta, timing, message = schol.pubmed.journal_lookup(issn)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.pubmed.name))
        self.assertTrue(meta["ISOAbbreviation"] == "PLoS ONE")


    def test_semantic_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"
        meta, timing, message = schol.semantic.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.semantic.name))
        self.assertTrue(meta["url"] == "https://www.semanticscholar.org/paper/690195fe2ab0fa093204a050ceb2f9fd1d1b2907")

        # error case
        doi = "10.00000/xxx"
        meta, timing, message = schol.semantic.publication_lookup(doi)
        self.assertTrue(meta == None)


    def test_unpaywall_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"
        meta, timing, message = schol.unpaywall.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.unpaywall.name))
        self.assertTrue(meta["doi_url"] == "https://doi.org/10.1016/j.appet.2017.07.006")

        # error case
        doi = "10.00000/xxx"
        meta, timing, message = schol.unpaywall.publication_lookup(doi)
        self.assertTrue(meta == None)


    def test_dissemin_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1016/j.appet.2017.07.006"
        meta, timing, message = schol.dissemin.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.dissemin.name))
        self.assertTrue(meta["paper"]["date"] == "2017-10-01")

        # error case
        doi = "10.00000/xxx"
        meta, timing, message = schol.dissemin.publication_lookup(doi)
        self.assertTrue(meta == None)


    def test_repec_handle_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Estimating the 'True' Cost of Job Loss: Evidence Using Matched Data from California 1991-2000"
        meta, timing, message = schol.repec.get_handle(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.repec.name))
        self.assertTrue(meta == "RePEc:cen:wpaper:09-14")


    def test_datacite_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.22002/d1.246"
        title = "In Situ Carbon Dioxide and Methane Mole Fractions from the Los Angeles Megacity Carbon Project"
        meta, timing, message = schol.datacite.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.datacite.name))
        self.assertTrue(meta["attributes"]["doi"] == doi)
        self.assertTrue(meta["attributes"]["titles"][0]["title"] == title)

        # error case
        doi = "10.00000/xxx"
        meta, timing, message = schol.datacite.publication_lookup(doi)
        self.assertTrue(meta == None)
        self.assertTrue("404" in message)


    def test_datacite_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        title = "Empirical analysis of potential improvements for high voltage protective algorithms"
        meta, timing, message = schol.datacite.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.datacite.name))
        self.assertTrue(meta and meta["id"] == "10.5281/zenodo.3635395")

        title = "ajso58tt849qp3g84h38pghq3974ut8gq9j9ht789" # Should be no matches
        meta, timing, message = schol.datacite.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.datacite.name))
        self.assertTrue(meta == None)


    def test_datacite_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "NOAA NASA"
        meta, timing, message = schol.datacite.full_text_search(search_term, limit=5, exact_match=True)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.datacite.name))
        self.assertTrue(len(meta) == 5)


    def test_datacite__format_exact_quote (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "NOAA NASA"
        exact_quote = schol.datacite._format_exact_quote(search_term)
        self.assertTrue(exact_quote == '"NOAA+NASA"')


    def test_core_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1371/journal.pone.0013969"
        title = "Caribbean corals in crisis: record thermal stress, bleaching, and mortality in 2005".lower()

        meta, timing, message = schol.core.publication_lookup(doi)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.core.name))
        self.assertTrue(meta["doi"] == doi)
        self.assertTrue(meta["title"].lower() == title)

        # error case
        doi = "10.00000/xxx"
        meta, timing, message = schol.core.publication_lookup(doi)
        self.assertTrue(meta == None)
        self.assertTrue("Not found" == message)


    def test_core_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        doi = "10.1371/journal.pone.0013969"
        title = "Caribbean corals in crisis: record thermal stress, bleaching, and mortality in 2005".lower()
        meta, timing, message = schol.core.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.core.name))
        self.assertTrue(meta and meta["doi"] == doi)

        title = "ajso58tt849qp3g84h38pghq3974ut8gq9j9ht789" # Should be no matches
        meta, timing, message = schol.core.title_search(title)

        print("\ntime: {:.3f} ms - {}".format(timing, schol.core.name))
        self.assertTrue(meta == None)
        self.assertTrue(message == "Not found")


    def test_core_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        search_term = "NASA NOAA coral"
        
        meta, timing, message = schol.core.full_text_search(search_term, limit=13) ##CORE limit value range: 10-100 
        print("\ntime: {:.3f} ms - {}".format(timing, schol.core.name))
        self.assertTrue(len(meta) == 13)

        meta, timing, message = schol.core.full_text_search(search_term, limit=2)  
        print("\ntime: {:.3f} ms - {}".format(timing, schol.core.name))
        self.assertTrue(len(meta) == 10)

        meta, timing, message = schol.core.full_text_search(search_term, limit=101)  
        print("\ntime: {:.3f} ms - {}".format(timing, schol.core.name))
        self.assertTrue(len(meta) == 10)


    def test_core_journal_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        issn = "1932-6203"

        meta, timing, message = schol.core.journal_lookup(issn)
        self.assertTrue(meta["title"] == "PLoS ONE")

        # error case
        meta, timing, message = schol.core.journal_lookup("0000-0000")
        self.assertTrue(meta == None)
        self.assertTrue(message == 'Not found')

if __name__ == "__main__":
    unittest.main()
