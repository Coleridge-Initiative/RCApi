#!/usr/bin/env python
# encoding: utf-8

from Bio import Entrez
from bs4 import BeautifulSoup
from collections import OrderedDict
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import cProfile
import configparser
import crossref_commons.retrieval
import csv
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
import warnings
import xmltodict


class _ScholInfra:
    """
    methods for accessing a specific Scholarly Infrastructure API
    """

    def __init__ (self, parent=None, name="Generic", api_url=None, cgi_url=None):
        self.parent = parent
        self.name = name
        self.api_url = api_url
        self.cgi_url = cgi_url
        self.api_obj = None


    def has_credentials (self):
        """
        returns `True` if the parent object's configuration includes
        the parameters required as credentials for a given discovery
        service API
        """
        return True


    @classmethod
    def _mark_elapsed_time (cls, t0):
        """
        mark the elapsed time since the start of the API access method
        """
        t1 = time.time()
        return (t1 - t0) * 1000.0


    def report_perf (self, timing):
        """
        report the performance for a given API response
        """
        print("\ntime: {:.3f} ms - {}".format(timing, self.name))


    def _get_api_url (self, *args):
        """
        construct a URL to query the API
        """
        return self.api_url.format(*args)


    @classmethod
    def _get_xml_node_value (cls, root, *name):
        """
        return the named value from an XML node, if it exists
        """
        if len(name) == 1:
            node = root.find(name[0])
        elif len(name) == 2:
            node = root.find(name[0], name[1])

        if not node:
            return None
        elif len(node.text) < 1:
            return None
        else:
            return node.text.strip()


    @classmethod
    def _clean_title (cls, title):
        """
        minimal set of string transformations so that a title can be
        compared consistently across API providers
        """
        return re.sub("\s+", " ", title.strip(" \"'?!.,")).lower()


    @classmethod
    def title_match (cls, title0, title1):
        """
        within reason, do the two titles match?
        """
        if not title0 or not title1:
            return False
        else:
            return cls._clean_title(title0) == cls._clean_title(title1)


    def full_text_search (self, search_term, limit=None, exact_match=True):
        """
        Perform a full-text search for publications using the API for
        one of the discovery services. Parse the returned metadata
        while measuring the performance of API responses. Also, trap
        and report errors in consistent ways.

        :param search_term: Query terms for full-text search of publications.
        :type search_term: str.

        :param limit: Maximum number of search responses to return.
        :type limit: int.

        :param exact_match: Some APIs allow a flag to turn off exact matches.
        :type limit: bool.

        :returns: list (_ScholInfraResponse(meta, timing, message))
            - meta - publication JSON text from search results.
            - timing - elasped system time in seconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return [_ScholInfraResponse(self, meta, timing, message)]


    def title_search (self, title):
        """
        Attempt to locate metadata for a publication based on its
        title, using the API for one of the discovery services. Parse
        the returned metadata while measuring the performance of API
        responses. Also, trap and report errors in consistent ways.

        :param title: Query term to locate a specific publications.
        :type title: str.

        :returns: _ScholInfraResponse(meta, timing, message)
            - meta - publication JSON text from search results.
            - timing - elasped system time in milliseconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return _ScholInfraResponse(self, meta, timing, message)


    def publication_lookup (self, identifier):
        """
        Attempt to locate metadata for a publication based on its
        persistent identifier, using the API for one of the discovery
        services. In this case the persistent identifier is a DOI.
        Parse the returned metadata while measuring the performance of
        API responses. Also, trap and report errors in consistent
        ways.

        :param identifier: DOI used to locate a specific publications.
        :type identifier: str.

        :returns: _ScholInfraResponse(self, meta, timing, message))
            - meta - publication JSON text from search results.
            - timing - elasped system time in milliseconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return _ScholInfraResponse(self, meta, timing, message) 


    def journal_lookup (self, identifier):
        """
        Attempt to locate metadata for a journal based on its
        persistent identifier, using the API for one of the discovery
        services. In this case the persistent identifier is an ISSN.
        Parse the returned metadata while measuring the performance of
        API responses. Also, trap and report errors in consistent
        ways.

        :param identifier: ISSN used to locate a specific journal.
        :type identifier: str.

        :returns: tuple (meta, timing, message)
            - meta - JSON list of search results.
            - timing - elasped system time in milliseconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return _ScholInfraResponse(self, meta, timing, message, False)


class _ScholInfra_EuropePMC (_ScholInfra):
    """
    https://europepmc.org/RestfulWebService
    """

    def title_search (self, title):
        """
        parse metadata from XML returned from the EuropePMC API query
        """
        meta = None
        timing = 0.0
        message = None

        try:
            t0 = time.time()
            url = self._get_api_url(urllib.parse.quote(title))
            response = requests.get(url).text
            soup = BeautifulSoup(response, "html.parser")

            if self.parent.logger:
                self.parent.logger.debug(soup.prettify())

            meta = OrderedDict()
            result_list = soup.find_all("result")

            for result in result_list:
                if self.parent.logger:
                    self.parent.logger.debug(result)

                result_title = self._get_xml_node_value(result, "title")

                if self.title_match(title, result_title):
                    val = self._get_xml_node_value(result, "doi")

                    if val:
                        meta["doi"] = val

                    val = self._get_xml_node_value(result, "pmcid")

                    if val:
                        meta["pmcid"] = val
                        has_pdf = self._get_xml_node_value(result, "haspdf")

                        if has_pdf == "Y":
                            meta["pdf"] = "http://europepmc.org/articles/{}?pdf=render".format(meta["pmcid"])

                    val = self._get_xml_node_value(result, "journaltitle")

                    if val:
                        meta["journal"] = val

                    val = self._get_xml_node_value(result, "authorstring")

                    if val:
                        meta["authors"] = val.split(", ")

                    source = self._get_xml_node_value(result, "source"),
                    pmid = self._get_xml_node_value(result, "pmid")

                    if (source and pmid) and not isinstance(source, tuple):
                        meta["url"] = "https://europepmc.org/article/{}/{}".format(source, pmid)

            if len(meta) < 1:
                meta = None

        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {title}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_EuropePMC(self, meta, timing, message)


class _ScholInfra_OpenAIRE (_ScholInfra):
    """
    https://develop.openaire.eu/
    """

    def title_search (self, title):
        """
        parse metadata from XML returned from the OpenAIRE API query
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        url = self._get_api_url() + "title={}".format(urllib.parse.quote(title))
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html.parser")

        if self.parent.logger:
            self.parent.logger.debug(soup.prettify())

        meta = OrderedDict()

        for result in soup.find_all("oaf:result"):
            result_title = self._get_xml_node_value(result, "title")

            if self.title_match(title, result_title):
                meta["doi"] = self._get_xml_node_value(result, "pid", {"classname": "doi"})
                meta["title"] = self._get_xml_node_value(result, "title")
                meta["url"] = self._get_xml_node_value(result, "url")
                meta["authors"] = [a.text for a in result.find_all("creator")]
                meta["open"] = len(result.find_all("bestaccessright", {"classid": "OPEN"})) > 0

                timing = self._mark_elapsed_time(t0)
                return _ScholInfraResponse_OpenAIRE(self, meta, timing, message)
        
        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_OpenAIRE(self, None, timing, message)


    def full_text_search (self, search_term, limit=None, exact_match=None):
        """
        parse metadata from XML returned from the OpenAIRE API query
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        base_url = self._get_api_url() + "keywords={}".format(urllib.parse.quote(search_term))
        
        if limit:
            search_url = base_url + "&size={}".format(limit)
        else:
            response = requests.get(base_url).text
            soup = BeautifulSoup(response, "html.parser")
            limit_response = int(soup.find("total").text)
            search_url = base_url + "&size={}".format(limit_response)
        
        response = requests.get(search_url).text
        soup = BeautifulSoup(response, "html.parser")
        meta = soup.find_all("oaf:result")

        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_OpenAIRE(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_OpenAIRE(self, meta, timing, message)]
    

class _ScholInfra_SemanticScholar (_ScholInfra):
    """
    http://api.semanticscholar.org/
    """

    def publication_lookup (self, identifier):
        """
        parse metadata returned from a Semantic Scholar API query
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        url = self._get_api_url(identifier)
        meta = json.loads(requests.get(url).text)

        if not meta or len(meta) < 1 or "error" in meta:
            meta = None

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_SemanticScholar(self, meta, timing, message)


class _ScholInfra_Unpaywall (_ScholInfra):
    """
    https://unpaywall.org/products/api
    """

    def publication_lookup (self, identifier):
        """
        construct a URL to query the API for Unpaywall
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        email = self.parent.config["DEFAULT"]["email"]

        url = self._get_api_url(identifier, email)
        meta = json.loads(requests.get(url).text)

        if not meta or len(meta) < 1 or "error" in meta:
            meta = None

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_Unpaywall(self, meta, timing, message)


class _ScholInfra_dissemin (_ScholInfra):
    """
    https://dissemin.readthedocs.io/en/latest/api.html
    """

    def publication_lookup (self, identifier):
        """
        parse metadata returned from a dissemin API query
        """
        meta = None
        timing = 0.0
        message = None

        try:
            t0 = time.time()
            url = self._get_api_url(identifier)
            meta = json.loads(requests.get(url).text)

            if not meta or len(meta) < 1 or "error" in meta:
                meta = None

        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_dissemin(self, meta, timing, message)


class _ScholInfra_Dimensions (_ScholInfra):
    """
    https://docs.dimensions.ai/dsl/
    """

    def has_credentials (self):
        required_creds = set([ "email", "dimensions_password" ])
        return required_creds.issubset(self.parent.config["DEFAULT"])


    def _login (self):
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


    def _run_query (self, query):
        """
        run one Dimensions API query, and first login if needed
        """
        self._login()
        return self.api_obj.query(query)


    def title_search (self, title):
        """
        parse metadata from a Dimensions API query
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        enc_title = title.replace('"', '').replace(":", " ").strip()
        query = 'search publications in title_only for "\\"{}\\"" return publications[all]'.format(enc_title)

        self._login()
        response = self._run_query(query)

        if hasattr(response, "publications"):
            for meta in response.publications:
                result_title = meta["title"]

                if self.title_match(title, result_title):
                    if self.parent.logger:
                        self.parent.logger.debug(meta)

                    if len(meta) > 0:
                        timing = self._mark_elapsed_time(t0)
                        return _ScholInfraResponse_Dimensions(self, meta, timing, message)
        
        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_Dimensions(self, None, timing, message)


    def full_text_search (self, search_term, limit=None, exact_match=True):
        """
        parse metadata from a Dimensions API full-text search
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()

        if not limit:
            query = 'search publications in full_data_exact for "\\"{}\\"" return publications[all] limit 1000'.format(search_term)

            if exact_match == False:
                query = 'search publications in full_data_exact for "{}" return publications[all] limit 1000'.format(search_term)

        else:
            query = 'search publications in full_data_exact for "\\"{}\\"" return publications[all] limit {}'.format(search_term,limit)

            if exact_match == False:
                query = 'search publications in full_data_exact for "{}" return publications[all] limit {}'.format(search_term,limit)

        self._login()
        response = self._run_query(query)
        meta = response.publications
        
        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_Dimensions(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_Dimensions(self, meta, timing, message)]


class _ScholInfra_RePEc (_ScholInfra):
    """
    https://ideas.repec.org/api.html
    """

    def has_credentials (self):
        required_creds = set([ "repec_token" ])
        return required_creds.issubset(self.parent.config["DEFAULT"])


    def _get_cgi_url (self, title):
        """
        construct a URL to query the CGI for RePEc
        """
        enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))
        return self.cgi_url.format(enc_title)

    # TODO make REPEC conform to the base-class methods
    def get_handle (self, title):
        """
        to use the RePEc API, first obtain a handle for a publication
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        url = self._get_cgi_url(title)
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html.parser")

        if self.parent.logger:
            self.parent.logger.debug(soup.prettify())

        ol = soup.find("ol", {"class": "list-group"})
        results = ol.findChildren()

        if len(results) > 0:
            li = results[0]

            if self.parent.logger:
                self.parent.logger.debug(li)

            # TODO: can we perform a title search here?
            meta = li.find("i").get_text()

        timing = self._mark_elapsed_time(t0)
        return meta, timing, message


    def get_meta (self, handle):
        """
        pull RePEc metadata based on the handle
        """
        meta = None
        timing = 0.0
        message = None

        try:
            t0 = time.time()
            token = self.parent.config["DEFAULT"]["repec_token"]
            url = self._get_api_url(token, handle)
            meta = json.loads(requests.get(url).text)

            if not meta or len(meta) < 1:
                meta = None
            if meta == [{'error': 2}]:
                raise Exception('Issue when fetching metadata: ', meta)
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {handle}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_RePEc(self, meta, timing, message)


class _ScholInfra_SSRN (_ScholInfra):
    """
    https://www.ssrn.com/index.cfm/en/
    """

    def _lookup_url (self, url):
        """
        extract the structured metadata from a rendered URL
        """
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

        if len(meta) < 1:
            meta = None

        return meta
    

    def publication_lookup (self, identifier):
        """
        parse metadata returned from an SSRN publication page using a DOI
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        url = self._get_api_url(identifier)

        if "ssrn" in url:    
            meta = self._lookup_url(url)
            timing = self._mark_elapsed_time(t0)

            if not meta or len(meta) < 1:
                meta = None

        return _ScholInfraResponse_SSRN(self, meta, timing, message)


    def title_search (self, title):
        """
        title search for SSRN
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        ssrn_homepage = "https://www.ssrn.com/index.cfm/en/"

        chrome_path = self.parent.config["DEFAULT"]["chrome_exe_path"]
        chrome_options = Options()  
        chrome_options.add_argument("--headless")  

        browser = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
        browser.get(ssrn_homepage)

        class_name = "form-control"
        search = browser.find_element_by_class_name(class_name)

        search.send_keys(title)
        search.send_keys(Keys.RETURN)

        search_url = browser.current_url
        search_url_result = browser.get(search_url)

        # TODO: Fix Exception thrown when element not found
        result_element = browser.find_element_by_xpath("//*[@class='title optClickTitle']")
        url = result_element.get_attribute("href")
        browser.quit()

        meta = self._lookup_url(url)

        if not meta or len(meta) < 1:
            meta = None

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_SSRN(self, meta, timing, message)


class _ScholInfra_Crossref (_ScholInfra):

    def publication_lookup (self, identifier):
        """
        parse metadata returned from Crossref API given a DOI
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        meta = crossref_commons.retrieval.get_publication_as_json(identifier)
        
        if not meta or len(meta) < 1:
            meta = None

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_Crossref(self, meta, timing, message)


    def title_search (self, title):
        """
        parse metadata returned from Crossref API given a title
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        query = "query.bibliographic={}".format(urllib.parse.quote(title))
        url = self._get_api_url(query)

        response = requests.get(url).text
        json_response = json.loads(response)

        items = json_response["message"]["items"]
        first_item = items[0] if len(items) > 0 else {}
        titles = first_item.get("title", [])
        result_title = titles[0] if len(titles) > 0 else None

        if self.title_match(title, result_title):
            meta = first_item

            if self.parent.logger:
                self.parent.logger.debug(meta)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_Crossref(self, meta, timing, message)


    def full_text_search (self, search_term, limit=None, exact_match=None):
        """
        search the Crossref API using a given term e.g. NHANES. 
        Note that Crossref doesn't support exact string matching 
        for multiple terms within strings.
        See https://github.com/CrossRef/rest-api-doc/issues/143
        """
        meta = None
        timing = 0.0
        message = None

        if not limit:
            limit = 1000

        t0 = time.time()
        query = "query=%22{}%22/type/journal-article&rows={}".format(urllib.parse.quote(search_term), limit)
        url = self._get_api_url(query)

        response = requests.get(url).text
        json_response = json.loads(response)
        meta = json_response["message"].get('items')

        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_Crossref(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_Crossref(self, meta, timing, message)]


class _ScholInfra_PubMed (_ScholInfra):
    """
    parse metadata returned from PubMed's Entrez API given a title
    """

    def title_search (self, title):
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()     
        Entrez.email = self.parent.config["DEFAULT"]["email"]

        handle = Entrez.read(Entrez.esearch(
                db="pubmed",
                retmax=100,
                term="\"{}\"".format(title),
                field = "title",
                retmode = "xml"
                ))
        
        id_list = handle.get("IdList", [])
        search_id = id_list[0] if len(id_list) > 0 else None

        if search_id:
            fetch_result = Entrez.efetch(db="pubmed", id=search_id, retmode="xml")
            data = fetch_result.read()
            fetch_result.close()

            xml = xmltodict.parse(data)
            parsed = json.loads(json.dumps(xml))

            if "PubmedArticle" in parsed["PubmedArticleSet"]:
                parsed = parsed["PubmedArticleSet"]["PubmedArticle"]
                result_title = parsed["MedlineCitation"]["Article"]["ArticleTitle"]

                if self.title_match(title, result_title):
                    if parsed and len(parsed) > 0:
                        meta = parsed

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_PubMed(self, meta, timing, message)


    def _full_text_get_ids (self, search_term, limit=None):
        try:
            limit = int(limit)
        except ValueError: #if limit can't be casted into int
            limit = None

        id_list = None
        Entrez.email = self.parent.config["DEFAULT"]["email"]

        query_return = Entrez.read(Entrez.egquery(term="\"{}\"".format(search_term)))
        response_count = int([d for d in query_return["eGQueryResult"] if d["DbName"] == "pubmed"][0]["Count"])

        if response_count > 0:
            if limit == None:
                handle = Entrez.read(Entrez.esearch(
                    db="pubmed",
                    retmax=response_count,
                    term="\"{}\"".format(search_term)
                    )
                )

                id_list = handle["IdList"]

            elif limit > 0:
                handle = Entrez.read(Entrez.esearch(
                    db="pubmed",
                    retmax=limit,
                    term="\"{}\"".format(search_term)
                    )
                )

                id_list = handle["IdList"]

        return id_list


    def full_text_search (self, search_term, limit=None, exact_match=None):
        """
        PubMed full-text search
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        Entrez.email = self.parent.config["DEFAULT"]["email"]
        id_list = self._full_text_get_ids(search_term, limit)
        
        if id_list and len(id_list) > 0:
            id_list = ",".join(id_list)

            fetch_result = Entrez.efetch(
                db="pubmed",
                id=id_list,
                retmode = "xml"
                )

            data = fetch_result.read()
            fetch_result.close()

            xml = xmltodict.parse(data)
            meta_list = json.loads(json.dumps(xml))
            meta = meta_list["PubmedArticleSet"]["PubmedArticle"]
                
        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_PubMed(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_PubMed(self, meta, timing, message)]

                        
    def journal_lookup (self, identifier):
        """
        use the NCBI discovery service for ISSN lookup
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()

        try:
            url = "https://www.ncbi.nlm.nih.gov/nlmcatalog/?report=xml&format=text&term={}".format(identifier)
            response = requests.get(url).text

            soup = BeautifulSoup(response, "html.parser")
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
                            message = f"NCBI bad XML format: no JrXML element for ISSN {identifier}"
                            return None, timing, message

                    meta = ncbi["JrXml"]["Serial"]
                    #pprint.pprint(meta)

        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_PubMed(self, meta, timing, message, False)


class _ScholInfra_DataCite (_ScholInfra): 
    
    def _format_exact_quote (self, search_term):
        #exact_terms = ["+" + term for term in search_term.split(" ")]
        #return urllib.parse.quote(" ".join(exact_terms), safe="+")
        return '"' + urllib.parse.quote_plus(search_term.strip()) + '"'


    def publication_lookup (self, identifier):
        """
        parse metadata returned from DataCite API given a DOI
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        url = self._get_api_url("/" + identifier)

        response = requests.get(url)

        if response.status_code == 200:
            json_response = json.loads(response.text)
            meta = json_response["data"]
        else:
            meta = None
            message = response.text

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_Datacite(self, meta, timing, message)

    
    def title_search (self, title):
        """
        parse metadata from the DataCite API query
        """
        meta = None
        timing = 0.0
        message = None

        t0 = time.time()
        query = self._format_exact_quote(title)
        url = self._get_api_url("?resource-type-id=text&query=titles.title:{}".format(query))
        
        try:
            response = requests.get(url)            

            if response.status_code == 200:
                json_response = json.loads(response.text)
                entries = json_response["data"]
                max_score = 0.0

                for entry in entries:
                    titles = entry.get("attributes")["titles"]

                    for title_obj in titles:
                        s = SequenceMatcher(None, title_obj["title"], title)

                        if (s.ratio() > max_score):
                            meta = entry
                            max_score = s.ratio()

                if max_score < 0.9: # a heuristic/guess -- we need to analyze this
                    meta = None

            else:
                meta = None
                message = response.text

        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {title}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_Datacite(self, meta, timing, message)


    def full_text_search (self, search_term, limit=None, exact_match=None):
        """
        DataCite full-text search
        """
        meta = None
        timing = 0.0
        message = None 
        t0 = time.time()

        if exact_match:
            url = self._get_api_url("?resource-type-id=text&query={}".format(self._format_exact_quote(search_term)))
        else:
            url = self._get_api_url("?resource-type-id=text&query={}".format(urllib.parse.quote_plus(search_term)))

        if limit:
            url = url + "&page[size]={}".format(limit)

        response = requests.get(url)

        if response.status_code == 200:
            json_response = json.loads(response.text)
            meta = json_response["data"]
        else:
            meta = None
            message = response.text

        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_Datacite(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_Datacite(self, meta, timing, message)]


class _ScholInfra_CORE (_ScholInfra): 

    def has_credentials (self):
        required_creds = set([ "core_apikey" ])
        return required_creds.issubset(self.parent.config["DEFAULT"])


    def _get_core_apikey (self): 
        key = self.parent.config["DEFAULT"]["core_apikey"]
        return {"apiKey": key}


    def publication_lookup (self, identifier):
        """
        parse metadata returned from CORE API given a DOI
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()
        try: 
            params = self._get_core_apikey()
            search_query = urllib.parse.quote("doi:\""+ identifier + "\"")

            url = self._get_api_url("articles", "search", search_query + "?" + urllib.parse.urlencode(params) )
            response = requests.get(url)

            if response.status_code == 200:
                json_response = json.loads(response.text)

                if (json_response["status"] == "OK"):
                    meta = json_response["data"][0]
                else:
                    meta = None
                    message = json_response["status"]
            else:
                meta = None
                message = response.text
        except: 
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_CORE(self, meta, timing, message)


    def title_search (self, title):
        """
        parse metadata from the CORE API query
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()

        try:
            params = self._get_core_apikey()
            search_query = urllib.parse.quote("title:\""+ title + "\"")

            url = self._get_api_url("articles", "search", search_query + "?" + urllib.parse.urlencode(params) )
            response = requests.get(url)

            if response.status_code == 200:
                json_response = json.loads(response.text)

                if (json_response["status"] == "OK"):
                    for entry in  json_response["data"]:
                        if entry["title"].lower() == title.lower():
                            meta = entry
                            break
                else:
                    meta = None
                    message = json_response["status"]
            else:
                meta = None
                message = response.text
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {title}"
            print(message)
        
        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_CORE(self, meta, timing, message)     


    def full_text_search (self, search_term, limit=None, exact_match=None):
        """
        CORE full-text search
        """
        meta = None
        timing = 0.0
        message = None 
        t0 = time.time()

        try:
            params = self._get_core_apikey()

            if limit:
                params["pageSize"] = limit
            if exact_match:
                search_query = '"' + urllib.parse.quote_plus(search_term.strip()) + '"'
            else:
                search_query = urllib.parse.quote(search_term)
            
            url = self._get_api_url("articles", "search", search_query + "?" + urllib.parse.urlencode(params) )
            response = requests.get(url)

            if response.status_code == 200:
                json_response = json.loads(response.text)

                if (json_response["status"] == "OK"):
                    meta = json_response["data"]
                else:
                    meta = None
                    message = json_response["status"]
            else:
                meta = None
                message = response.text
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {search_term}"
            print(message)
                    
        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_CORE(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_CORE(self, meta, timing, message)]

    
    def journal_lookup (self, identifier):
        meta = None
        timing = 0.0
        message = None 
        t0 = time.time()

        try:
            params = self._get_core_apikey()
            url = self._get_api_url("journals", "get", identifier + "?" + urllib.parse.urlencode(params) )
            response = requests.get(url)

            if response.status_code == 200:
                json_response = json.loads(response.text)

                if (json_response["status"] == "OK"):
                    meta = json_response["data"]
                else:
                    meta = None
                    message = json_response["status"]
            else:
                meta = None
                message = response.text
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)
        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_CORE(self, meta, timing, message, False)


class _ScholInfra_ORCID (_ScholInfra): 

    def publication_lookup (self, identifier):
        """
        parse metadata returned from ORCID API given an ORCID identifier
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()

        try:
            url = self._get_api_url(identifier, "works")
            response = requests.get(url)
            xml = xmltodict.parse(response.text, xml_attribs=False)

            if xml is not None:
                xml = (xml["activities:works"] or {}).get("activities:group")
                meta = json.loads(json.dumps(xml))
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_ORCID(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_ORCID(self, meta, timing, message)]


    def affiliations (self, identifier):
        """
        fetches individual's employment details from ORCID 
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()

        try:
            url = self._get_api_url(identifier, "employments")
            response = requests.get(url)
            xml = xmltodict.parse(response.text, xml_attribs=False)

            if xml is not None:
                xml = (xml["activities:employments"] or {}).get("employment:employment-summary")
                meta = json.loads(json.dumps(xml))
        except: 
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_ORCID(self, meta, timing, message, False)


    def funding (self, identifier):
        """
        fetches individuals funding details from ORCID 
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()

        try:
            url = self._get_api_url(identifier, "fundings")
            response = requests.get(url)
            xml = xmltodict.parse(response.text, xml_attribs=False)

            if xml is not None:
                xml = (xml["activities:fundings"] or {}).get("activities:group")
                meta = json.loads(json.dumps(xml))
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_ORCID(self, meta, timing, message, False)


class _ScholInfra_NSF_PAR (_ScholInfra): 

    def _request_data (self, search_url, export_url): 
        with requests.Session() as session:
            chrome_path = self.parent.config["DEFAULT"]["chrome_exe_path"]                
            chrome_options = Options()  
            chrome_options.add_argument("--headless")  

            browser = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
            browser.get(search_url)        

            request_cookies_browser = browser.get_cookies()
            [session.cookies.set(c["name"], c["value"]) for c in request_cookies_browser]

            resp = session.post(export_url)
            reader = csv.DictReader(io.StringIO(resp.content.decode("utf-8"))) 
            json_data = json.dumps(list(reader))
            json_data = json.loads(json_data)  

            browser.quit()      
            session.close()

        return json_data


    def full_text_search (self, search_term, limit=None, exact_match=True):
        """
        NSF PAR full text search for publications
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()

        if exact_match:
            warnings.warn("Exact Match is not supported by {}, ignoring this argument".format(self.name))

        try: 
            search_url = self._get_api_url("search", "fulltext:" + urllib.parse.quote(search_term))
            export_url = self._get_api_url("export/format:csv", "fulltext:" + urllib.parse.quote(search_term))

            json_data = self._request_data(search_url, export_url)
            
            if limit and limit > 0 and limit < len(json_data):
                meta = json_data[:limit]
            else:
                meta = json_data
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {search_term}"
            print(message) 

        timing = self._mark_elapsed_time(t0)
        return [_ScholInfraResponse_NSF_PAR(self, data, timing, message) for data in meta] if meta else [_ScholInfraResponse_NSF_PAR(self, None, timing, message)]


    def title_search (self, title):
        """
        NSF PAR title search for a publication
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()
        
        try:
            search_url = self._get_api_url("search", "title:" + urllib.parse.quote(title))
            export_url = self._get_api_url("export/format:csv", "title:" + urllib.parse.quote(title))
 
            json_data = self._request_data(search_url, export_url)
            
            if  json_data and len(json_data) > 0:
                meta = json_data[0]
            else:
                meta = None
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {title}"
            print(message) 
        
        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_NSF_PAR(self, meta, timing, message)


    def publication_lookup (self, identifier):
        """
        NSF PAR publication look using DOI string
        """
        meta = None
        timing = 0.0
        message = None
        t0 = time.time()
        
        try:
            search_url = self._get_api_url("search", "identifier:" + urllib.parse.quote(identifier))
            export_url = self._get_api_url("export/format:csv", "identifier:" + urllib.parse.quote(identifier))
 
            json_data = self._request_data(search_url, export_url)
            
            if  json_data and len(json_data) > 0:
                meta = json_data[0]
            else:
                meta = None
        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {identifier}"
            print(message) 
        
        timing = self._mark_elapsed_time(t0)
        return _ScholInfraResponse_NSF_PAR(self, meta, timing, message)

    
######################################################################
## managed responses

class _ScholInfraResponse:
    """
    manage the response from a specific Scholarly Infrastructure API
    """

    def __init__ (self, parent=None, meta=None, timing=None, message=None, is_publication=True):
        self.parent = parent
        self.meta = meta
        self.timing = timing
        self.message = message
        self.is_publication = is_publication


    def doi(self):
        raise NotImplementedError


    def title(self):
        raise NotImplementedError


    def authors(self):
        raise NotImplementedError


    def url(self):
        raise NotImplementedError


    def journal(self):
        raise NotImplementedError


    def serialize(self):
        return self.meta


class _ScholInfraResponse_EuropePMC(_ScholInfraResponse):
    
    def doi(self):
        return self.meta["doi"] if self.meta else None


    def journal(self):
        return self.meta["journal"] if self.meta else None


    def authors(self):
        return self.meta["authors"] if self.meta else None


class _ScholInfraResponse_OpenAIRE(_ScholInfraResponse):
    
    def doi(self):
        return self.meta["doi"] if self.meta else None


    def title(self):
        return self.meta["title"] if self.meta else None


    def authors(self):
        return self.meta["authors"] if self.meta else None


    def url(self):
        return self.meta["url"] if self.meta else None


class _ScholInfraResponse_SemanticScholar(_ScholInfraResponse):

    def doi(self):
        return self.meta["doi"] if self.meta else None


    def title(self):
        return self.meta["title"] if self.meta else None


    def authors(self):
        return self.meta["authors"] if self.meta else None


    def url(self):
        return self.meta["url"] if self.meta else None


    def journal(self):
        return self.meta["venue"] if self.meta else None


class _ScholInfraResponse_Unpaywall(_ScholInfraResponse):
    pass


class _ScholInfraResponse_dissemin(_ScholInfraResponse):
    pass


class _ScholInfraResponse_Dimensions(_ScholInfraResponse):
    
    def doi(self):
        return self.meta["doi"] if self.meta else None


    def title(self):
        return self.meta["title"] if self.meta else None


    def authors(self):
        return self.meta["authors"] if self.meta else None


    def url(self):
        return self.meta["linkout"] if self.meta else None


    def journal(self):
        return self.meta.get("journal", {}).get("title")


class _ScholInfraResponse_RePEc(_ScholInfraResponse):
    pass


class _ScholInfraResponse_SSRN(_ScholInfraResponse):
    
    def doi(self):
        return self.meta.get("doi") if self.meta else None


    def title(self):
        return self.meta.get("title") if self.meta else None


    def authors(self):
        return self.meta.get("authors") if self.meta else None


class _ScholInfraResponse_Crossref(_ScholInfraResponse):
    
    def doi(self):
        return self.meta.get("DOI") if self.meta else None


    def title(self):
        title = self.meta.get("title") if self.meta else None
        return title[0] if title and len(title) > 0 else None


    def authors(self):
        return self.meta.get("author") if self.meta else None


    def url(self):
        return self.meta.get("URL") if self.meta else None


    def journal(self):
        journal = self.meta.get("container-title") if self.meta else None
        return journal[0] if journal and len(journal) > 0 else None


class _ScholInfraResponse_PubMed(_ScholInfraResponse):

    def pdmid(self):
        return self.meta.get("MedlineCitation", {}).get("PMID", {}).get("#text") if self.meta else None


    def doi(self):
        try:
            pid_list = self.meta.get("MedlineCitation", {}).get("Article", {}).get("ELocationID")
            if isinstance(pid_list,list):
                dois = [d["#text"] for d in pid_list if d["@EIdType"] == "doi"]
                if len(dois) > 0:
                    return dois[0]

            if isinstance(pid_list,dict):
                if pid_list["@EIdType"] == "doi":
                   return pid_list["#text"]
        except:
            return None


    def title(self):
        title = None
        article_meta = self.meta.get("MedlineCitation", {}).get("Article") if self.meta else None
        if article_meta and article_meta.get("ArticleTitle"):
            if type(article_meta.get("ArticleTitle")) is str:
                title = article_meta.get("ArticleTitle")
            elif type(article_meta.get("ArticleTitle")) is dict:
                title = article_meta.get("ArticleTitle", {}).get("#text")
        return title


    def journal(self):
        if self.is_publication:
            article_meta = self.meta.get("MedlineCitation", {}).get("Article", {}) if self.meta else {}
            return article_meta.get("Journal", {}).get("Title")
        else:
            return self.meta.get("Title") if self.meta else None


    def issn(self):
        if self.is_publication:
            return self.meta.get("ISOAbbreviation") if self.meta else None
        else: 
            return self.meta.get("ISSN", {}).get("#text") if self.meta else None


class _ScholInfraResponse_Datacite(_ScholInfraResponse):

    def doi(self):
        return self.meta.get("attributes", {}).get("doi") if self.meta else None


    def title(self):
        titles = self.meta.get("attributes", {}).get("titles", []) if self.meta else []
        return  titles[0].get("title") if titles else None
        

    def authors(self):
        authors = self.meta.get("attributes", {}).get("creators", []) if self.meta else []
        return [creator["name"] for creator in authors] if authors else None


    def url(self):
        return self.meta.get("attributes",{}).get("url") if self.meta else None


    def journal(self):
        return self.meta.get("attributes",{}).get("publisher") if self.meta else None


class _ScholInfraResponse_CORE(_ScholInfraResponse):

    def doi(self):
        if self.is_publication:
            return self.meta.get("doi") if self.meta else None
        return None

    def title(self):
        if self.is_publication:
            return self.meta.get("title") if self.meta else None
        else:
            return self.meta.get("title") if self.meta else None


    def authors(self):
        if self.is_publication:
            return self.meta.get("authors") if self.meta else None
        return None


    def url(self):
        if self.is_publication:
            return self.meta.get("downloadUrl") if self.meta else None
        return None


    def journal(self):
        if self.is_publication:
            return self.meta.get("publisher") if self.meta else None
        return None


class _ScholInfraResponse_ORCID(_ScholInfraResponse):

    def title(self):
        if self.is_publication:
            return self.meta.get("work:work-summary", {}).get("work:title", {}).get("common:title") if self.meta else None
        return None


    def authors(self):
        if self.is_publication:
            return self.meta.get("work:work-summary", {}).get("common:source", {}).get("common:source-name") if self.meta else None
        return None 


class _ScholInfraResponse_NSF_PAR(_ScholInfraResponse):

    def doi(self):
        return self.meta.get("DOI") if self.meta else None


    def title(self):
        return self.meta.get("TITLE") if self.meta else None


    def authors(self):
        return self.meta.get("AUTHORS") if self.meta else None


    def journal(self):
        return self.meta.get("JOURNAL_NAME") if self.meta else None


    def issn(self):
        return self.meta.get("ISSN") if self.meta else None


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

        self.crossref = _ScholInfra_Crossref(
            parent=self,
            name="Crossref",
            api_url ="https://api.crossref.org/works?{}"
            )
        
        self.europepmc = _ScholInfra_EuropePMC(
            parent=self,
            name="EuropePMC",
            api_url="https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={}"
            )

        self.openaire = _ScholInfra_OpenAIRE(
            parent=self,
            name="OpenAIRE",
            api_url="http://api.openaire.eu/search/publications?"
            )

        self.pubmed = _ScholInfra_PubMed(
            parent=self,
            name="PubMed"
            )

        self.semantic = _ScholInfra_SemanticScholar(
            parent=self,
            name="Semantic Scholar",
            api_url = "http://api.semanticscholar.org/v1/paper/{}"
            )

        self.unpaywall = _ScholInfra_Unpaywall(
            parent=self,
            name="Unpaywall",
            api_url = "https://api.unpaywall.org/v2/{}?email={}"
            )

        self.dissemin = _ScholInfra_dissemin(
            parent=self,
            name="dissemin",
            api_url = "https://dissem.in/api/{}"
            )

        self.dimensions = _ScholInfra_Dimensions(
            parent=self,
            name="Dimensions",
            )

        self.repec = _ScholInfra_RePEc(
            parent=self,
            name="RePEc",
            api_url = "https://api.repec.org/call.cgi?code={}&getref={}",
            cgi_url = "https://ideas.repec.org/cgi-bin/htsearch?q={}"
            )

        self.ssrn = _ScholInfra_SSRN(
            parent=self,
            name="SSRN",
            api_url ="https://doi.org/{}"
            )

        self.datacite = _ScholInfra_DataCite(
            parent=self,
            name="DataCite",
            api_url="https://api.datacite.org/dois{}"
            )

        self.core = _ScholInfra_CORE(
            parent=self,
            name="CORE",
            api_url="https://core.ac.uk:443/api-v2/{}/{}/{}"
            )

        self.orcid = _ScholInfra_ORCID (
            parent=self,
            name="ORCID",
            api_url="https://pub.orcid.org/v2.0/{}/{}"
            )

        self.nsfPar = _ScholInfra_NSF_PAR(
            parent=self,
            name="NSF PAR",
            api_url="https://par.nsf.gov/{}/{}"
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
