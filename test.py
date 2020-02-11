#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import pprint
import unittest

   
class TestOpenAPIs (unittest.TestCase):

    ######################################################################
    ## PubMed family of APIs

    def test_europepmc_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.europepmc

        title = "Zebrafish models: Gaining insight into purinergic signaling and neurological disorders"
        expected = "OrderedDict([('doi', '10.1016/j.pnpbp.2019.109770'), ('journal', 'Prog Neuropsychopharmacol Biol Psychiatry'), ('authors', ['Nabinger DD', 'Altenhofen S', 'Bonan CD.'])])"

        if source.has_credentials():
            meta, timing, message = source.title_search(title)
            source.report_perf(timing)
            self.assertTrue(repr(meta) == expected)


    def test_pubmed_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.pubmed

        title = "Climate-change-driven accelerated sea-level rise detected in the altimeter era"
        expected = "29440401"

        if source.has_credentials():
            meta, timing, message = source.title_search(title)
            source.report_perf(timing)
            self.assertTrue(meta["MedlineCitation"]["PMID"]["#text"] == expected)


    def test_pubmed_journal_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.pubmed

        issn = "1932-6203"
        expected = "PLoS ONE"

        if source.has_credentials():
            meta, timing, message = source.journal_lookup(issn)
            source.report_perf(timing)
            self.assertTrue(meta["ISOAbbreviation"] == expected)


    ######################################################################
    ## Scholix family of APIs

    def test_crossref_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.crossref

        doi = "10.1503/cmaj.170880"
        expected = "Relation between household food insecurity and breastfeeding in Canada"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            source.report_perf(timing)
            self.assertTrue(meta["title"][0] == expected)


    def test_crossref_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.crossref

        title = "Relation between household food insecurity and breastfeeding in Canada"
        expected = "10.1503/cmaj.170880"

        if source.has_credentials():
            meta, timing, message = source.title_search(title)
            source.report_perf(timing)
            self.assertTrue(meta["DOI"] == expected)
        

    def test_crossref_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.crossref

        search_term = "NHANES"
        expected = 100

        if source.has_credentials():
            meta, timing, message = source.full_text_search(search_term, limit=expected)
            source.report_perf(timing)
            self.assertTrue(meta["total-results"] >= expected)


    def test_datacite_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.datacite

        doi = "10.22002/d1.246"
        title = "In Situ Carbon Dioxide and Methane Mole Fractions from the Los Angeles Megacity Carbon Project"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(response.title() == title)
            self.assertTrue(response.authors == ["Verhulst, Kristal"])

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            self.assertTrue(response.meta == None)
            self.assertTrue("404" in response.message)


    def test_datacite_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.datacite

        title = "Empirical analysis of potential improvements for high voltage protective algorithms"
        expected = "10.5281/zenodo.3635395"

        if source.has_credentials():
            response = source.title_search(title)
            self.assertTrue(response.meta and response.meta["id"] == expected)
            self.assertTrue(response.title() == title)

        # error case
        title = "ajso58tt849qp3g84h38pghq3974ut8gq9j9ht789" # Should be no matches

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.meta == None)


    def test_datacite_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.datacite

        search_term = "NOAA NASA"
        expected = 5

        if source.has_credentials():
            response = source.full_text_search(search_term, limit=expected, exact_match=True)
            source.report_perf(response.timing)
            self.assertTrue(len(response.meta) == expected)


    def test_datacite__format_exact_quote (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.datacite

        search_term = "NOAA NASA"
        expected = '"NOAA+NASA"'

        exact_quote = source._format_exact_quote(search_term)
        self.assertTrue(exact_quote == expected)


    def test_openaire_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.openaire

        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        expected = "OrderedDict([('url', 'https://europepmc.org/articles/PMC5574185/'), ('authors', ['Taillie, Lindsey Smith', 'Ng, Shu Wen', 'Xue, Ya', 'Harding, Matthew']), ('open', True)])"

        if source.has_credentials():
            meta, timing, message = source.title_search(title)
            source.report_perf(timing)
            self.assertTrue(repr(meta) == expected)

    
    def test_openaire_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.openaire

        search_term = "NHANES"
        expected = 100

        if source.has_credentials():
            meta, timing, message = source.full_text_search(search_term, limit=expected)
            source.report_perf(timing)
            self.assertTrue(len(meta) >= expected)


    ######################################################################
    ## Digital Science family of APIs

    def test_dimensions_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.dimensions

        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
        expected = "10.1016/j.appet.2017.07.006"

        if source.has_credentials():
            meta, timing, message = source.title_search(title)
            source.report_perf(timing)
            self.assertTrue(meta["doi"] == expected)


    def test_dimensions_full_text_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.dimensions

        search_term = "the French paradox"
        expected = "Food Chemistry"

        if source.has_credentials():
            meta, timing, message = source.full_text_search(search_term, limit=20, exact_match=True)
            source.report_perf(timing)

            for pub in meta:
                if pub["doi"] == "10.1016/j.foodchem.2019.125340":
                    self.assertTrue(pub["journal"]["title"] == expected)
                    return

            self.assertTrue("DOI not found" == "")


    ######################################################################
    ## Unpaywall family of APIs

    def test_unpaywall_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.unpaywall

        doi = "10.1016/j.appet.2017.07.006"
        expected = "https://doi.org/10.1016/j.appet.2017.07.006"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            source.report_perf(timing)
            self.assertTrue(meta["doi_url"] == expected)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            self.assertTrue(meta == None)


    def test_dissemin_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.dissemin

        doi = "10.1016/j.appet.2017.07.006"
        expected = "2017-10-01"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            source.report_perf(timing)
            self.assertTrue(meta["paper"]["date"] == expected)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            self.assertTrue(meta == None)


    def test_semantic_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.semantic

        doi = "10.1016/j.appet.2017.07.006"
        expected = "https://www.semanticscholar.org/paper/690195fe2ab0fa093204a050ceb2f9fd1d1b2907"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            source.report_perf(timing)
            self.assertTrue(meta["url"] == expected)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            meta, timing, message = source.publication_lookup(doi)
            self.assertTrue(meta == None)


    ######################################################################
    ## Misc. family of APIs

    def test_repec_handle_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.repec

        title = "Estimating the 'True' Cost of Job Loss: Evidence Using Matched Data from California 1991-2000"
        expected = "RePEc:cen:wpaper:09-14"

        if source.has_credentials():
            meta, timing, message = source.get_handle(title)
            source.report_perf(timing)
            self.assertTrue(meta == expected)


if __name__ == "__main__":
    unittest.main()
