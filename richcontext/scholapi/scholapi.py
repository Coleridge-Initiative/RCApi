#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
from collections import OrderedDict
import configparser
import json
import re
import requests
import sys
import time
import traceback
import urllib.parse


class ScholInfraAPI:
    """
    API integrations for federating metadata lookup across multiple
    scholarly infrastructure providers
    """

    def __init__ (self, config_file="rc.cfg"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)


    @classmethod
    def get_xml_node_value (cls, root, name):
        """
        return the named value from an XML node, if it exists
        """
        node = root.find(name)
        return (node.text if node else None)


    @classmethod
    def clean_title (cls, title):
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
        return cls.clean_title(title0) == cls.clean_title(title1)


    ######################################################################
    ## EuropePMC

    EUROPEPMC_API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={}"

    @classmethod
    def europepmc_get_api_url (cls, title):
        """
        construct a URL to query the API for EuropePMC
        """
        return cls.EUROPEPMC_API_URL.format(urllib.parse.quote(title))


    def europepmc_title_search (self, title):
        """
        parse metadata from XML returned from the EuropePMC API query
        """
        url = ScholInfraAPI.europepmc_get_api_url(title)
        response = requests.get(url).text
        soup = BeautifulSoup(response,  "html.parser")
        #print(soup.prettify())

        meta = OrderedDict()
        result_list = soup.find_all("result")

        for result in result_list:
            #print(result)
            result_title = ScholInfraAPI.get_xml_node_value(result, "title")

            if ScholInfraAPI.title_match(title, result_title):
                meta["doi"] = ScholInfraAPI.get_xml_node_value(result, "doi")
                meta["pmcid"] = ScholInfraAPI.get_xml_node_value(result, "pmcid")
                meta["journal"] = ScholInfraAPI.get_xml_node_value(result, "journaltitle")
                meta["authors"] = ScholInfraAPI.get_xml_node_value(result, "authorstring").split(", ")

                if ScholInfraAPI.get_xml_node_value(result, "haspdf") == "Y":
                    meta["pdf"] = "http://europepmc.org/articles/{}?pdf=render".format(meta["pmcid"])

        return meta


    ######################################################################
    ## openAIRE

    OPENAIRE_API_URL = "http://api.openaire.eu/search/publications?title={}"

    @classmethod
    def openaire_get_api_url (cls, title):
        """
        construct a URL to query the API for OpenAIRE
        """
        return cls.OPENAIRE_API_URL.format(urllib.parse.quote(title))


    def openaire_title_search (self, title):
        """
        parse metadata from XML returned from the OpenAIRE API query
        """
        url = ScholInfraAPI.openaire_get_api_url(title)
        response = requests.get(url).text
        soup = BeautifulSoup(response,  "html.parser")
        #print(soup.prettify())

        meta = OrderedDict()

        for result in soup.find_all("oaf:result"):
            result_title = ScholInfraAPI.get_xml_node_value(result, "title")

            if ScholInfraAPI.title_match(title, result_title):
                meta["url"] = ScholInfraAPI.get_xml_node_value(result, "url")
                meta["authors"] = [a.text for a in result.find_all("creator")]
                meta["open"] = len(result.find_all("bestaccessright",  {"classid": "OPEN"})) > 0
                break

        return meta


    ######################################################################
    ## RePEc API

    REPEC_CGI_URL = "https://ideas.repec.org/cgi-bin/htsearch?q={}"
    REPEC_API_URL = "https://api.repec.org/call.cgi?code={}&getref={}"

    @classmethod
    def repec_get_cgi_url (cls, title):
        """
        construct a URL to query the CGI for RePEc
        """
        enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))
        return cls.REPEC_CGI_URL.format(enc_title)


    @classmethod
    def repec_get_api_url (cls, handle, token):
        """
        construct a URL to query the API for RePEc
        """
        return cls.REPEC_API_URL.format(token, handle)


    def repec_get_handle (self, title):
        """
        to use the RePEc API, first obtain a handle for a publication
        """
        url = ScholInfraAPI.repec_get_cgi_url(title)
        response = requests.get(url).text
        soup = BeautifulSoup(response,  "html.parser")
        #print(soup.prettify())

        ol = soup.find("ol", {"class": "list-group"})
        results = ol.findChildren()

        if len(results) > 0:
            li = results[0]
            handle = li.find("i").get_text()
            return handle
        else:
            return None


    def repec_get_meta (self, token, handle):
        """
        pull RePEc metadata based on the handle
        """
        try:
            url = ScholInfraAPI.repec_get_api_url(token, handle)
            response = requests.get(url).text
            meta = json.loads(response)
            return meta

        except:
            print(traceback.format_exc())
            print("ERROR: {}".format(handle))
            return None


    ######################################################################
    ## Semantic Scholar API

    SEMANTIC_API_URL = "http://api.semanticscholar.org/v1/paper/{}"

    @classmethod
    def semantic_get_api_url (cls, identifier):
        """
        construct a URL to query the API for Semantic Scholar
        """
        return cls.SEMANTIC_API_URL.format(identifier)


    def semantic_publication_lookup (self, identifier):
        """
        parse metadata returned from a Semantic Scholar API query
        """
        url = ScholInfraAPI.semantic_get_api_url(identifier)
        meta = requests.get(url).text
        return json.loads(meta)


    ######################################################################
    ## Unpaywall API

    UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{}?email={}"

    @classmethod
    def unpaywall_get_api_url (cls, doi, email):
        """
        construct a URL to query the API for Unpaywall
        """
        return cls.UNPAYWALL_API_URL.format(doi, email)


    def unpaywall_publication_lookup (self, doi, email):
        """
        parse metadata returned from an Unpaywall API query
        """
        url = ScholInfraAPI.unpaywall_get_api_url(doi, email)
        meta = requests.get(url).text
        return json.loads(meta)


    ######################################################################
    ## dissemin API

    DISSEMIN_API_URL = "https://dissem.in/api/{}"

    @classmethod
    def dissemin_get_api_url (cls, doi):
        """
        construct a URL to query the dissemin API
        """
        return cls.DISSEMIN_API_URL.format(doi)


    def dissemin_publication_lookup (self, doi):
        """
        parse metadata returned from a dissemin API query
        """
        url = ScholInfraAPI.dissemin_get_api_url(doi)
        meta = requests.get(url).text
        return json.loads(meta)


######################################################################
## main entry point (not used)

if __name__ == "__main__":
    schol = ScholInfraAPI(config_file="rc.cfg")
    print([ (k, v) for k, v in schol.config["DEFAULT"].items()])
