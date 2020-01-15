#!/usr/bin/env python
# encoding: utf-8

from Bio import Entrez
from bs4 import BeautifulSoup
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import cProfile
import configparser
import crossref_commons.retrieval
import dimcli
import json
import io
import logging
import pprint
import pstats
import re
import requests
import requests_cache
import sys
import time
import traceback
import urllib.parse
import xmltodict


class ScholInfra:
    """
    methods for accessing a specific Scholarly Infrastructure API
    """

    def __init__ (self, parent=None, name="Generic", api_url=None, cgi_url=None):
        self.parent = parent
        self.name = name
        self.api_url = api_url
        self.cgi_url = cgi_url

        self.api_obj = None
        self.elapsed_time = 0.0


    def get_xml_node_value (self, root, name):
        """
        return the named value from an XML node, if it exists
        """
        node = root.find(name)

        if not node:
            return None
        elif len(node.text) < 1:
            return None
        else:
            return node.text.strip()


    def clean_title (self, title):
        """
        minimal set of string transformations so that a title can be
        compared consistently across API providers
        """
        return re.sub("\s+", " ", title.strip(" \"'?!.,")).lower()


    def title_match (self, title0, title1):
        """
        within reason, do the two titles match?
        """
        if not title0 or not title1:
            return False
        else:
            return self.clean_title(title0) == self.clean_title(title1)


    def get_api_url (self, *args):
        """
        construct a URL to query the API
        """
        return self.api_url.format(*args)


    def mark_time (self, t0):
        """
        mark the elapsed time since the start of the API access method
        """
        t1 = time.time()
        self.elapsed_time = (t1 - t0) * 1000.0


class ScholInfra_EuropePMC (ScholInfra):
    """
    https://europepmc.org/RestfulWebService
    """

    def title_search (self, title):
        """
        parse metadata from XML returned from the EuropePMC API query
        """
        try:
            t0 = time.time()

            url = self.get_api_url(urllib.parse.quote(title))
            response = requests.get(url).text

            soup = BeautifulSoup(response,  "html.parser")

            if self.parent.logger:
                self.parent.logger.debug(soup.prettify())

            meta = OrderedDict()
            result_list = soup.find_all("result")

            for result in result_list:
                if self.parent.logger:
                    self.parent.logger.debug(result)

                result_title = self.get_xml_node_value(result, "title")

                if self.title_match(title, result_title):
                    val = self.get_xml_node_value(result, "doi")

                    if val:
                        meta["doi"] = val

                    val = self.get_xml_node_value(result, "pmcid")

                    if val:
                        meta["pmcid"] = val
                        has_pdf = self.get_xml_node_value(result, "haspdf")

                        if has_pdf == "Y":
                            meta["pdf"] = "http://europepmc.org/articles/{}?pdf=render".format(meta["pmcid"])

                    val = self.get_xml_node_value(result, "journaltitle")

                    if val:
                        meta["journal"] = val

                    val = self.get_xml_node_value(result, "authorstring")

                    if val:
                        meta["authors"] = val.split(", ")

                    source = self.get_xml_node_value(result, "source"),
                    pmid = self.get_xml_node_value(result, "pmid")

                    if (source and pmid) and not isinstance(source, tuple):
                        meta["url"] = "https://europepmc.org/article/{}/{}".format(source, pmid)

            self.mark_time(t0)

            if len(meta) < 1:
                return None
            else:
                return meta
        except:
            print(traceback.format_exc())
            print("ERROR: {}".format(title))
            self.mark_time(t0)
            return None


class ScholInfra_OpenAIRE (ScholInfra):
    """
    https://develop.openaire.eu/
    """

    def title_search (self, title):
        """
        parse metadata from XML returned from the OpenAIRE API query
        """
        t0 = time.time()

        url = self.get_api_url() + "title={}".format(urllib.parse.quote(title))
        response = requests.get(url).text
        soup = BeautifulSoup(response,  "html.parser")

        if self.parent.logger:
            self.parent.logger.debug(soup.prettify())

        meta = OrderedDict()

        for result in soup.find_all("oaf:result"):
            result_title = self.get_xml_node_value(result, "title")

            if self.title_match(title, result_title):
                meta["url"] = self.get_xml_node_value(result, "url")
                meta["authors"] = [a.text for a in result.find_all("creator")]
                meta["open"] = len(result.find_all("bestaccessright",  {"classid": "OPEN"})) > 0

                self.mark_time(t0)
                return meta

        self.mark_time(t0)
        return None

    def full_text_search (self, search_term,nresults = None):
        """
        parse metadata from XML returned from the OpenAIRE API query
        """
        t0 = time.time()
        base_url = self.get_api_url() + "keywords={}".format(urllib.parse.quote(search_term))
        
        if nresults:
            search_url = base_url + '&size={}'.format(nresults)

        elif not nresults:
            response = requests.get(base_url).text
            soup = BeautifulSoup(response,  "html.parser")
            nresults_response = int(soup.find("total").text)
            search_url = base_url + '&size={}'.format(nresults_response)
        
        response = requests.get(search_url).text
        soup = BeautifulSoup(response,  "html.parser")
        pub_metadata = soup.find_all("oaf:result")
        self.mark_time(t0)
        return pub_metadata
    

class ScholInfra_SemanticScholar (ScholInfra):
    """
    http://api.semanticscholar.org/
    """

    def publication_lookup (self, identifier):
        """
        parse metadata returned from a Semantic Scholar API query
        """
        t0 = time.time()

        url = self.get_api_url(identifier)
        meta = json.loads(requests.get(url).text)

        self.mark_time(t0)

        if meta and len(meta) > 0:
            return meta
        else:
            return None


class ScholInfra_Unpaywall (ScholInfra):
    """
    https://unpaywall.org/products/api
    """

    def publication_lookup (self, identifier):
        """
        construct a URL to query the API for Unpaywall
        """
        t0 = time.time()

        email = self.parent.config["DEFAULT"]["email"]

        url = self.get_api_url(identifier, email)
        meta = json.loads(requests.get(url).text)

        self.mark_time(t0)

        if meta and len(meta) > 0:
            return meta
        else:
            return None


class ScholInfra_dissemin (ScholInfra):
    """
    https://dissemin.readthedocs.io/en/latest/api.html
    """

    def publication_lookup (self, identifier):
        """
        parse metadata returned from a dissemin API query
        """
        try:
            t0 = time.time()

            url = self.get_api_url(identifier)
            meta = json.loads(requests.get(url).text)

            self.mark_time(t0)

            if len(meta) < 1:
                return None
            elif "error" in meta:
                raise Exception(str(meta))
            else:
                return meta
        except:
            print(traceback.format_exc())
            print("ERROR: {}".format(identifier))
            self.mark_time(t0)
            return None


class ScholInfra_Dimensions (ScholInfra):
    """
    https://docs.dimensions.ai/dsl/
    """

    def login (self):
        """
        login to the Dimensions API through their 'DSL'
        """
        if not self.api_obj:
            dimcli.login(
                username=self.parent.config["DEFAULT"]["email"],
                password=self.parent.config["DEFAULT"]["dimensions_password"],
                verbose=False
                )

            self.api_obj = dimcli.Dsl(verbose=False)


    def run_query (self, query):
        """
        run one Dimensions API query, and first login if needed
        """
        self.login()
        return self.api_obj.query(query)


    def title_search (self, title):
        """
        parse metadata from a Dimensions API query
        """
        t0 = time.time()

        enc_title = title.replace('"', '\\"')
        query = 'search publications in title_only for "\\"{}\\"" return publications[all]'.format(enc_title)

        self.login()
        response = self.run_query(query)

        if hasattr(response, "publications"):
            for meta in response.publications:
                result_title = meta["title"]

                if self.title_match(title, result_title):
                    if self.parent.logger:
                        self.parent.logger.debug(meta)

                    self.mark_time(t0)

                    if len(meta) > 0:
                        return meta

        self.mark_time(t0)
        return None


    def full_text_search (self, search_term, exact_match = True, nresults = None):
        """
        parse metadata from a Dimensions API full-text search
        """
        t0 = time.time()
        if not nresults:
            query = 'search publications in full_data_exact for "\\"{}\\"" return publications[all] limit 1000'.format(search_term)

            if exact_match == False:
                query = 'search publications in full_data_exact for "{}" return publications[all] limit 1000'.format(search_term)
    
        if nresults:
            query = 'search publications in full_data_exact for "\\"{}\\"" return publications[all] limit {}'.format(search_term,nresults)

            if exact_match == False:
                query = 'search publications in full_data_exact for "{}" return publications[all] limit {}'.format(search_term,nresults)

            
        self.login()
        response = self.run_query(query)
        search_results = response.publications
        
        self.mark_time(t0)
        return search_results
        

class ScholInfra_RePEc (ScholInfra):
    """
    https://ideas.repec.org/api.html
    """

    def get_cgi_url (self, title):
        """
        construct a URL to query the CGI for RePEc
        """
        enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))
        return self.cgi_url.format(enc_title)


    def get_handle (self, title):
        """
        to use the RePEc API, first obtain a handle for a publication
        """
        t0 = time.time()

        url = self.get_cgi_url(title)
        response = requests.get(url).text
        soup = BeautifulSoup(response,  "html.parser")

        if self.parent.logger:
            self.parent.logger.debug(soup.prettify())

        ol = soup.find("ol", {"class": "list-group"})
        results = ol.findChildren()

        if len(results) > 0:
            li = results[0]

            if self.parent.logger:
                self.parent.logger.debug(li)

            # TODO: can we perform a title search here?
            handle = li.find("i").get_text()
            self.mark_time(t0)

            return handle

        self.mark_time(t0)
        return None


    def get_meta (self, handle):
        """
        pull RePEc metadata based on the handle
        """
        try:
            t0 = time.time()

            token = self.parent.config["DEFAULT"]["repec_token"]
            url = self.get_api_url(token, handle)
            meta = json.loads(requests.get(url).text)

            self.mark_time(t0)

            if meta and len(meta) > 0:
                return meta
            else:
                return None
        except:
            print(traceback.format_exc())
            print("ERROR: {}".format(handle))
            self.mark_time(t0)
            return None


class ScholInfra_SSRN (ScholInfra):
    """
    https://www.ssrn.com/index.cfm/en/
    """

    def url_lookup (self, url):
        """
        extract the structured metadata from a rendered URL
        """
        t0 = time.time()

        response = requests.get(url).text
        soup = BeautifulSoup(response, "html.parser")

        if self.parent.logger:
            self.parent.logger.debug(soup.prettify())

        meta = OrderedDict()

        meta["doi"] = soup.find("meta", {"name": "citation_doi"})["content"]
        meta["title"] = soup.find("meta", attrs={"name": "citation_title"})["content"]

        keywords_list_raw = soup.find("meta", attrs={"name": "citation_keywords"})["content"].split(";")
        keywords = [k.strip() for k in keywords_list_raw]
        meta["keywords"] = keywords

        auth_list = soup.find_all("meta", {"name":"citation_author"})
        authors = [a["content"] for a in auth_list]
        meta["authors"] = authors

        self.mark_time(t0)

        if len(meta) > 0:
            return meta
        else:
            return None
    

    def publication_lookup (self, identifier):
        """
        parse metadata returned from an SSRN publication page using a DOI
        """
        t0 = time.time()
        url = self.get_api_url(identifier)

        if "ssrn" in url:    
            meta = self.url_lookup(url)
            self.mark_time(t0)

            if meta and len(meta) > 0:
                return meta
            else:
                return None
        else:
            self.mark_time(t0)
            return None


    def title_search (self, title):
        """
        title search for SSRN
        """
        t0 = time.time()

        ssrn_homepage = "https://www.ssrn.com/index.cfm/en/"
        chrome_path=self.parent.config["DEFAULT"]["chrome_exe_path"]

        browser = webdriver.Chrome(executable_path=chrome_path)
        browser.get(ssrn_homepage)

        class_name = "form-control"
        search = browser.find_element_by_class_name(class_name)

        search.send_keys(title)
        search.send_keys(Keys.RETURN)

        search_url = browser.current_url
        search_url_result = browser.get(search_url)

        result_element = browser.find_element_by_xpath("//*[@class='title optClickTitle']")
        url = result_element.get_attribute("href")
        browser.quit()

        meta = self.url_lookup(url)
        self.mark_time(t0)

        if meta and len(meta) > 0:
            return meta
        else:
            return None


class ScholInfra_Crossref (ScholInfra):

    def publication_lookup (self, identifier):
        """
        parse metadata returned from Crossref API given a DOI
        """
        t0 = time.time()

        meta = crossref_commons.retrieval.get_publication_as_json(identifier)
        self.mark_time(t0)
        
        if meta and len(meta) > 0:
            return meta
        else:
            return None


    def title_search (self, title):
        """
        parse metadata returned from Crossref API given a title
        """
        t0 = time.time()

        query = "query.bibliographic={}".format(urllib.parse.quote(title))
        url = self.get_api_url(query)

        response = requests.get(url).text
        json_response = json.loads(response)

        meta = json_response["message"]["items"][0]
        result_title = meta["title"][0]

        if self.title_match(title, result_title):
            if self.parent.logger:
                self.parent.logger.debug(meta)

            self.mark_time(t0)
            return meta

        self.mark_time(t0)
        return None


    def full_text_search (self, search_term):
        """
        search the Crossref API using a given term e.g. NHANES. 
        Note that Crossref doesn't support exact string matching 
        for multiple terms within strings.
        See https://github.com/CrossRef/rest-api-doc/issues/143
        """
        t0 = time.time()

        query = "query=%22{}%22/type/journal-article&rows=1000".format(urllib.parse.quote(search_term))
        url = self.get_api_url(query)

        response = requests.get(url).text
        json_response = json.loads(response)
        search_results = json_response["message"]

        self.mark_time(t0)
        return search_results


class ScholInfra_PubMed (ScholInfra):
    """
    parse metadata returned from PubMed's Entrez API given a title
    """

    def title_search (self, title):
        t0 = time.time()
        
        Entrez.email = self.parent.config["DEFAULT"]["email"]

        handle = Entrez.read(Entrez.esearch(
                db="pubmed",
                retmax=100,
                term="\"{}\"".format(title),
                field = "title",
                retmode = "xml"
                ))
        
        search_id = handle["IdList"][0]
        
        fetch_result = Entrez.efetch(db="pubmed", id=search_id, retmode="xml")
        data = fetch_result.read()
        fetch_result.close()

        xml = xmltodict.parse(data)
        meta = json.loads(json.dumps(xml))

        if "PubmedArticle" in meta["PubmedArticleSet"]:
            meta = meta["PubmedArticleSet"]["PubmedArticle"]
            result_title = meta["MedlineCitation"]["Article"]["ArticleTitle"]

            if self.title_match(title, result_title):
                self.mark_time(t0)

                if meta and len(meta) > 0:
                    return meta

            self.mark_time(t0)
            return None


    def fulltext_id_search (self, search_term, nresults = None):
        Entrez.email = self.parent.config["DEFAULT"]["email"]

        query_return = Entrez.read(Entrez.egquery(term="\"{}\"".format(search_term)))
        response_count = int([d for d in query_return["eGQueryResult"] if d["DbName"] == "pubmed"][0]["Count"])

        if response_count > 0:
             if nresults == None:
                handle = Entrez.read(Entrez.esearch(db="pubmed",
                                                    retmax=response_count,
                                                    term="\"{}\"".format(search_term)
                                                    )
                                    )

                id_list = handle["IdList"]

            if nresults != None and nresults > 0 and isinstance(nresults, int):
                handle = Entrez.read(Entrez.esearch(db="pubmed",
                                                    retmax=nresults,
                                                    term="\"{}\"".format(search_term)
                                                    )
                                    )

                id_list = handle["IdList"]

            
            return id_list
        else:
            return None



    def full_text_search (self, search_term, nresults = None):
        t0 = time.time()
        
        Entrez.email = self.parent.config["DEFAULT"]["email"]
        id_list = self.fulltext_id_search(search_term)
        
        if id_list and len(id_list) > 0:
                id_list = ",".join(id_list)

                fetch_result = Entrez.efetch(db="pubmed",
                                             id=id_list,
                                             retmode = "xml"
                                             )

                data = fetch_result.read()
                fetch_result.close()

                xml = xmltodict.parse(data)
                meta_list = json.loads(json.dumps(xml))
                meta = meta_list["PubmedArticleSet"]["PubmedArticle"]
                
                self.mark_time(t0)
                return meta

                        
    def journal_lookup (self, issn):
        """
        use the NCBI discovery service for ISSN lookup
        """
        t0 = time.time()

        try:
            url = "https://www.ncbi.nlm.nih.gov/nlmcatalog/?report=xml&format=text&term={}".format(issn)
            response = requests.get(url).text

            soup = BeautifulSoup(response,  "html.parser")
            xml = soup.find("pre").text.strip()

            if len(xml) > 0:
                ## use an XML hack to workaround common formatting
                ## errors in the API respsonses from NCBI
                xml = "<fix>{}</fix>".format(xml)
                j = json.loads(json.dumps(xmltodict.parse(xml)))

                if "NCBICatalogRecord" in j["fix"]:
                    ncbi = j["fix"]["NCBICatalogRecord"]

                    if isinstance(ncbi, list):
                        if "JrXml" in ncbi[0]:
                            # ibid., XML hack
                            ncbi = ncbi[0]
                        elif len(ncbi) > 1 and "JrXml" in ncbi[1]:
                            ncbi = ncbi[1]
                        else:
                            # bad XML returned from the API call
                            return None, f"NCBI bad XML format: no JrXML element for ISSN {issn}"

                    meta = ncbi["JrXml"]["Serial"]
                    #pprint.pprint(meta)

                    self.mark_time(t0)
                    return meta, None

        except:
            print(traceback.format_exc())
            print(f"ERROR - NCBI failed lookup: {issn}")

        self.mark_time(t0)
        return None, None


######################################################################
## federated API access

class ScholInfraAPI:
    """
    API integrations for federating metadata lookup across multiple
    discovery service APIs from scholarly infrastructure providers
    """

    def __init__ (self, config_file="rc.cfg", logger=None):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.logger = logger

        # other initializations 
        requests_cache.install_cache("richcontext")

        self.crossref = ScholInfra_Crossref(
            parent=self,
            name="Crossref",
            api_url ="https://api.crossref.org/works?{}"
            )
        
        self.europepmc = ScholInfra_EuropePMC(
            parent=self,
            name="EuropePMC",
            api_url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={}"
            )

        self.openaire = ScholInfra_OpenAIRE(
            parent=self,
            name="OpenAIRE",
            api_url="http://api.openaire.eu/search/publications?title={}"
            )

        self.pubmed = ScholInfra_PubMed(
            parent=self,
            name="PubMed"
            )

        self.semantic = ScholInfra_SemanticScholar(
            parent=self,
            name="Semantic Scholar",
            api_url = "http://api.semanticscholar.org/v1/paper/{}"
            )

        self.unpaywall = ScholInfra_Unpaywall(
            parent=self,
            name="Unpaywall",
            api_url = "https://api.unpaywall.org/v2/{}?email={}"
            )

        self.dissemin = ScholInfra_dissemin(
            parent=self,
            name="dissemin",
            api_url = "https://dissem.in/api/{}"
            )

        self.dimensions = ScholInfra_Dimensions(
            parent=self,
            name="Dimensions",
            )

        self.repec = ScholInfra_RePEc(
            parent=self,
            name="RePEc",
            api_url = "https://api.repec.org/call.cgi?code={}&getref={}",
            cgi_url = "https://ideas.repec.org/cgi-bin/htsearch?q={}"
            )

        self.ssrn = ScholInfra_SSRN(
            parent=self,
            name="SSRN",
            api_url ="https://doi.org/{}"
            )


    ## profiling utilities

    def start_profiling (self):
        """start profiling"""
        pr = cProfile.Profile()
        pr.enable()

        return pr


    def stop_profiling (self, pr):
        """stop profiling and report"""
        pr.disable()

        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)

        ps.print_stats()
        print(s.getvalue())


######################################################################
## main entry point (not used)

if __name__ == "__main__":
    schol = ScholInfraAPI(config_file="rc.cfg")
    print([ (k, v) for k, v in schol.config["DEFAULT"].items()])
