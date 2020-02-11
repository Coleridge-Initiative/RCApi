#!/usr/bin/env python
# encoding: utf-8

from Bio import Entrez
from bs4 import BeautifulSoup
from collections import OrderedDict
from difflib import SequenceMatcher
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
    def _get_xml_node_value (cls, root, name):
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

        :returns: tuple (meta, timing, message)
            - meta - JSON list of search results.
            - timing - elasped system time in seconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return meta, timing, message


    def title_search (self, title):
        """
        Attempt to locate metadata for a publication based on its
        title, using the API for one of the discovery services. Parse
        the returned metadata while measuring the performance of API
        responses. Also, trap and report errors in consistent ways.

        :param title: Query term to locate a specific publications.
        :type title: str.

        :returns: tuple (meta, timing, message)
            - meta - JSON list of search results.
            - timing - elasped system time in milliseconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return meta, timing, message


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

        :returns: tuple (meta, timing, message)
            - meta - JSON list of search results.
            - timing - elasped system time in milliseconds.
            - message - an optional error message.
        """
        meta = None
        timing = 0.0
        message = None

        return meta, timing, message


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

        return meta, timing, message


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
        return meta, timing, message


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
                meta["url"] = self._get_xml_node_value(result, "url")
                meta["authors"] = [a.text for a in result.find_all("creator")]
                meta["open"] = len(result.find_all("bestaccessright", {"classid": "OPEN"})) > 0

                timing = self._mark_elapsed_time(t0)
                return meta, timing, message

        return None, timing, message


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
        return meta, timing, message
    

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
        return meta, timing, message


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
        return meta, timing, message


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
        return meta, timing, message


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
                        return meta, timing, message

        return None, timing, message


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
        return meta, timing, message
        

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

        except:
            print(traceback.format_exc())
            meta = None
            message = f"ERROR: {handle}"
            print(message)

        timing = self._mark_elapsed_time(t0)
        return meta, timing, message


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

        return meta, timing, message
    

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

        return meta, timing, message


    def title_search (self, title):
        """
        title search for SSRN
        """
        meta = None
        timing = 0.0
        message = None

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

        if not meta or len(meta) < 1:
            meta = None

        timing = self._mark_elapsed_time(t0)
        return meta, timing, message


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
        return meta, timing, message


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

        parsed = json_response["message"]["items"][0]
        result_title = parsed["title"][0]

        if self.title_match(title, result_title):
            meta = parsed

            if self.parent.logger:
                self.parent.logger.debug(meta)

        timing = self._mark_elapsed_time(t0)
        return meta, timing, message


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
        meta = json_response["message"]

        self._mark_elapsed_time(t0)
        return meta, timing, message


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
        
        search_id = handle["IdList"][0]
        
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
        return meta, timing, message


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
        return meta, timing, message

                        
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
        return meta, timing, message


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
        return meta, timing, message

    
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
        return meta, timing, message


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
        return meta, timing, message


######################################################################
## managed responses

class _ScholInfraResponse:
    """
    manage the response from a specific Scholarly Infrastructure API
    """

    def __init__ (self, parent=None, meta=None, timing=0, message=None):
        self.parent = parent
        self.meta = meta
        self.timing = timing
        self.message = message


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
