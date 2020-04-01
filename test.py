#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import pprint
import unittest
import warnings

   
def ignore_warnings (test_func):
    """see https://stackoverflow.com/questions/26563711/disabling-python-3-2-resourcewarning
    """
    def do_test (self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            test_func(self, *args, **kwargs)

    return do_test


class TestOpenAPIs (unittest.TestCase):

    ######################################################################
    ## PubMed family of APIs

    def test_europepmc_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.europepmc

        title = "Zebrafish models: Gaining insight into purinergic signaling and neurological disorders"
        expected = "OrderedDict([('doi', '10.1016/j.pnpbp.2019.109770'), ('journal', 'Prog Neuropsychopharmacol Biol Psychiatry'), ('authors', ['Nabinger DD', 'Altenhofen S', 'Bonan CD.'])])"

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(repr(response.meta) == expected)
            self.assertTrue(response.doi() == '10.1016/j.pnpbp.2019.109770')
            self.assertTrue(response.journal() == 'Prog Neuropsychopharmacol Biol Psychiatry')
            self.assertTrue(response.authors() == ['Nabinger DD', 'Altenhofen S', 'Bonan CD.'])


    def test_pubmed_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.pubmed

        title = "Climate-change-driven accelerated sea-level rise detected in the altimeter era."
        expected = "29440401"
        doi = "10.1073/pnas.1717312115"
        journal = "Proceedings of the National Academy of Sciences of the United States of America"

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.pdmid() == expected)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(response.title() == title)
            self.assertTrue(response.journal() == journal)
            self.assertTrue(response.issn() is None)

        title = "NOT_TO_BE_FOUND"
        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.meta is None)
            self.assertTrue(response.pdmid() is None)
            self.assertTrue(response.doi() is None)
            self.assertTrue(response.title() is None)
            self.assertTrue(response.journal() is None)
            self.assertTrue(response.issn() is None)


    def test_pubmed_journal_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.pubmed

        issn = "1932-6203"
        expected = "PLoS ONE".lower()

        if source.has_credentials():
            response = source.journal_lookup(issn)
            source.report_perf(response.timing)
            self.assertTrue(response.pdmid() == None)
            self.assertTrue(response.doi() == None)
            self.assertTrue(response.title() == None)
            self.assertTrue(response.journal().lower() == expected)
            self.assertTrue(response.issn() == issn)

    
    def test_pubmed_full_text_search (self):
        #TODO
        pass

    ######################################################################
    ## Scholix family of APIs

    def test_crossref_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.crossref

        doi = "10.1503/cmaj.170880"
        expected = "Relation between household food insecurity and breastfeeding in Canada"
        num_authors = 4
        url = "http://dx.doi.org/10.1503/cmaj.170880"
        journal = "Canadian Medical Association Journal"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(response.title() == expected)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(len(response.authors()) == num_authors)
            self.assertTrue(response.url() == url)
            self.assertTrue(response.journal() == journal)


    def test_crossref_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.crossref

        title = "Relation between household food insecurity and breastfeeding in Canada"
        expected = "10.1503/cmaj.170880"

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.doi() == expected)
        
        title = "D"
        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.meta is None)


    def test_crossref_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.crossref

        search_term = "NHANES"
        expected = 100

        if source.has_credentials():
            responses = source.full_text_search(search_term, limit=expected)
            source.report_perf(responses[0].timing)
            self.assertTrue(len(responses) >= expected)


    def test_datacite_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.datacite

        doi = "10.22002/d1.246"
        title = "In Situ Carbon Dioxide and Methane Mole Fractions from the Los Angeles Megacity Carbon Project"
        url = "https://data.caltech.edu/records/246"
        journal = "CaltechDATA"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(response.title() == title)
            self.assertTrue(response.authors() == ["Verhulst, Kristal"])
            self.assertTrue(response.url() == url)
            self.assertTrue(response.journal() == journal)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            self.assertTrue(response.serialize() == None)
            self.assertTrue("404" in response.message)
            self.assertTrue(response.doi() is None)
            self.assertTrue(response.title() is None)
            self.assertTrue(response.authors() is None)
            self.assertTrue(response.url() is None)
            self.assertTrue(response.journal() is None)


    def test_datacite_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.datacite

        title = "Empirical analysis of potential improvements for high voltage protective algorithms"
        expected = "10.5281/zenodo.3635395"
        journal = "Zenodo"
        author = "López, David"
        url = "https://zenodo.org/record/3635395"

        if source.has_credentials():
            response = source.title_search(title)
            self.assertTrue(response.meta and response.meta["id"] == expected)
            self.assertTrue(response.doi() == expected)
            self.assertTrue(response.title() == title)
            self.assertTrue(author in response.authors())
            self.assertTrue(response.url() == url)
            self.assertTrue(response.journal() == journal)

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
            responses = source.full_text_search(search_term, limit=expected, exact_match=True)
            source.report_perf(responses[0].timing)
            self.assertTrue(len(responses) == expected)


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

        doi = "10.1016/j.appet.2017.07.006"
        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases"
        url = "https://europepmc.org/articles/PMC5574185/"
        authors = ["Taillie, Lindsey Smith", "Ng, Shu Wen", "Xue, Ya", "Harding, Matthew"]

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(response.title() == title)
            self.assertTrue(response.url() == url)
            self.assertTrue(response.authors() == authors)
            self.assertTrue(response.meta["open"])

    
    def test_openaire_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.openaire

        search_term = "NHANES"
        expected = 100

        if source.has_credentials():
            responses = source.full_text_search(search_term, limit=expected)
            source.report_perf(responses[0].timing)
            self.assertTrue(len(responses) >= expected)


    ######################################################################
    ## Digital Science family of APIs

    def test_dimensions_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.dimensions

        title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases"
        expected = "10.1016/j.appet.2017.07.006"
        url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5574185"
        journal = "Appetite"

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.doi() == expected)
            self.assertTrue(response.title() == title)
            self.assertTrue(response.url() == url)
            self.assertTrue(response.journal() == journal)


    def test_dimensions_full_text_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.dimensions

        search_term = "the French paradox"
        expected = "Food Chemistry"

        if source.has_credentials():
            responses = source.full_text_search(search_term, limit=20, exact_match=True)
            source.report_perf(responses[0].timing)

            for response in responses:
                if response.doi() == "10.1016/j.foodchem.2019.126123":
                    self.assertTrue(response.journal() == expected)
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
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(response.meta["doi_url"] == expected)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            self.assertTrue(response.meta == None)


    def test_dissemin_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.dissemin

        doi = "10.1016/j.appet.2017.07.006"
        expected = "2017-10-01"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(response.meta["paper"]["date"] == expected)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            self.assertTrue(response.meta == None)


    def test_semantic_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.semantic

        doi = "10.1016/j.appet.2017.07.006"
        expected = "https://www.semanticscholar.org/paper/690195fe2ab0fa093204a050ceb2f9fd1d1b2907"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(response.url() == expected)
            self.assertTrue(response.doi() == doi)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            self.assertTrue(response.meta == None)


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


    def test_core_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.core

        doi = "10.1371/journal.pone.0013969"
        title = "Caribbean corals in crisis: record thermal stress, bleaching, and mortality in 2005".lower()

        # NB: there may be multiple "correct" responses for the
        # following -- this test case has some instability
        urls = ["https://core.ac.uk/download/pdf/143863779.pdf", "https://core.ac.uk/download/pdf/51094169.pdf"]
        journals = ["Public Library of Science", "NSUWorks"]

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)

            self.assertTrue(response.doi() == doi)
            self.assertTrue(response.title().lower() == title)
            self.assertTrue(response.url() in urls)
            self.assertTrue(response.journal() in journals)

        # error case
        doi = "10.00000/xxx"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            self.assertTrue(response.meta == None)
            self.assertTrue(response.doi() == None)
            self.assertTrue(response.title() == None)
            self.assertTrue(response.url() == None)
            self.assertTrue(response.authors() == None)
            self.assertTrue(response.journal() == None)
            self.assertTrue("Not found" == response.message)


    def test_core_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.core

        doi = "10.1371/journal.pone.0013969"
        title = "Caribbean corals in crisis: record thermal stress, bleaching, and mortality in 2005".lower()
        url = "https://core.ac.uk/download/pdf/51094169.pdf"
        author = "Eakin, C. Mark"
        journal = "NSUWorks"

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(response.title().lower() == title)
            self.assertTrue(response.url() == url)
            self.assertTrue(author in response.authors())
            self.assertTrue(response.journal() == journal)

        # error case
        title = "ajso58tt849qp3g84h38pghq3974ut8gq9j9ht789" # Should be no matches

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(response.meta == None)
            self.assertTrue(response.message == "Not found")


    def test_core_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.core

        search_term = "NASA NOAA coral"
        
        if source.has_credentials():
            # CORE limit value range: 10-100 
            responses = source.full_text_search(search_term, limit=13)
            source.report_perf(responses[0].timing)
            self.assertTrue(len(responses) == 13)

            responses = source.full_text_search(search_term, limit=2)  
            source.report_perf(responses[0].timing)
            self.assertTrue(len(responses) == 10)

            responses = source.full_text_search(search_term, limit=101)  
            source.report_perf(responses[0].timing)
            self.assertTrue(len(responses) == 10)


    def test_core_journal_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.core

        issn = "1932-6203"
        expected = "PLoS ONE"

        if source.has_credentials():
            response = source.journal_lookup(issn)
            source.report_perf(response.timing)
            self.assertTrue(response.title() == expected)

        # error case
        issn = "0000-0000"

        if source.has_credentials():
            response = source.journal_lookup(issn)
            source.report_perf(response.timing)
            self.assertTrue(response.meta == None)
            self.assertTrue(response.message == 'Not found')


    @ignore_warnings
    def test_nsf_par_fulltext_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.nsfPar

        ## please note, these numbers may change as new publications are added
        search_term = "NASA NOAA coral"
        responses = source.full_text_search(search_term, limit=13, exact_match=True)
        source.report_perf(responses[0].timing)
        self.assertTrue(len(responses) == 13)

        responses = source.full_text_search(search_term, limit=-1, exact_match=True)
        source.report_perf(responses[0].timing)
        self.assertTrue(len(responses) == 15)

        responses = source.full_text_search(search_term, limit=1000, exact_match=True)
        source.report_perf(responses[0].timing)
        self.assertTrue(len(responses) == 15)

        #Won't find any
        search_term = "dlkadngeonr3q0984gqn839g"
        responses = source.full_text_search(search_term, limit=13)
        source.report_perf(responses[0].timing)
        self.assertTrue(len(responses) == 1)
        self.assertTrue(responses[0].meta is None)


    @ignore_warnings
    def test_nsf_par_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.nsfPar

        ##Please note, these numbers may change as new publications are added
        title = "Essential ocean variables for global sustained observations of biodiversity and ecosystem changes"
        doi = "10.1111/gcb.14108"
        response = source.title_search(title)
        source.report_perf(response.timing)
        self.assertTrue(response.doi() == doi)

        #Won't find any
        title = "dlkadngeonr3q0984gqn839g"
        response = source.title_search(title)
        source.report_perf(response.timing)
        self.assertTrue(response.meta is None)


    @ignore_warnings
    def test_nsf_par_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.nsfPar

        ##Please note, these numbers may change as new publications are added
        title = "Essential ocean variables for global sustained observations of biodiversity and ecosystem changes"
        doi = "10.1111/gcb.14108"
        response = source.publication_lookup(doi)
        
        source.report_perf(response.timing)
        self.assertTrue(response.doi() == doi)
        self.assertTrue(response.title() == title)

        #Error case
        doi = "10.00000/xxx"
        response = source.publication_lookup(title)
        source.report_perf(response.timing)
        self.assertTrue(response.meta is None)
    
    
    def test_orcid_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.orcid

        orcid = "0000-0002-8139-2960" #Julia Lane
        response = source.publication_lookup(orcid)
        source.report_perf(response[0].timing)
        #This number may change in the future
        self.assertTrue(len(response) == 137)

        orcid = "0000-0002-0735-6312"
        response = source.publication_lookup(orcid)
        source.report_perf(response[0].timing)
        #This number may change in the future
        self.assertTrue(response[0].meta is None)


    def test_orcid_affiliations (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.orcid

        orcid = "0000-0002-8139-2960" #Julia Lane
        response = source.affiliations(orcid)
        source.report_perf(response.timing)
        #This number may change in the future
        self.assertTrue(len(response.meta) == 3)

        orcid = "0000-0002-0735-6312"
        response = source.affiliations(orcid)
        source.report_perf(response.timing)
        #This number may change in the future
        self.assertTrue(response.meta is None)


    def test_orcid_funding (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.orcid

        orcid = "0000-0002-8139-2960" #Julia Lane
        response = source.funding(orcid)
        source.report_perf(response.timing)
        #This number may change in the future
        self.assertTrue(len(response.meta) == 17)

        orcid = "0000-0002-0735-6312"
        response = source.funding(orcid)
        source.report_perf(response.timing)
        #This number may change in the future
        self.assertTrue(response.meta is None)   


    def test_ssrn_publication_lookup (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.ssrn

        doi = "10.2139/ssrn.2898991"
        authors = ['Freedman, Matthew', 'Kuhns, Annemarie']
        expected = "OrderedDict([('doi', '10.2139/ssrn.2898991'), ('title', 'Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit'), ('keywords', ['place-based policies', 'retail food', 'tax incentives', 'community health', 'regression discontinuity']), ('authors', ['Freedman, Matthew', 'Kuhns, Annemarie'])])"

        if source.has_credentials():
            response = source.publication_lookup(doi)
            source.report_perf(response.timing)
            self.assertTrue(repr(response.meta) == expected)
            self.assertTrue(response.doi() == doi)
            self.assertTrue(all(author in authors for author in response.authors()))


    def test_ssrn_title_search (self):
        schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
        source = schol.ssrn

        title = "Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit"
        expected = "OrderedDict([('doi', '10.2139/ssrn.2898991'), ('title', 'Supply-Side Subsidies to Improve Food Access and Dietary Outcomes: Evidence from the New Markets Tax Credit'), ('keywords', ['place-based policies', 'retail food', 'tax incentives', 'community health', 'regression discontinuity']), ('authors', ['Freedman, Matthew', 'Kuhns, Annemarie'])])"

        if source.has_credentials():
            response = source.title_search(title)
            source.report_perf(response.timing)
            self.assertTrue(repr(response.meta) == expected)
            self.assertTrue(response.title() == title)


if __name__ == "__main__":
    unittest.main()
