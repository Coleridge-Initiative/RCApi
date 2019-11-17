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


CONFIG_FILE = "rc.cfg"

CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)


######################################################################
## utility functions

def get_xml_node_value (root, name):
    """
    return the value from an XML node, if it exists
    """
    node = root.find(name)

    if node:
        return node.text
    else:
        return None


def clean_title (title):
    return re.sub("\s+", " ", title.strip(" \"'?!.,")).lower()


def title_match (title0, title1):
    """
    within reason, do the two titles match?
    """
    return clean_title(title0) == clean_title(title1)


######################################################################
## EuropePMC

EUROPEPMC_API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={}"


def europepmc_get_api_url (title):
    """
    construct a URL to query the API for EuropePMC
    """
    return EUROPEPMC_API_URL.format(urllib.parse.quote(title))


def europepmc_title_search (title):
    """
    parse metadata from XML returned from the EuropePMC API query
    """
    url = europepmc_get_api_url(title)
    response = requests.get(url).text
    soup = BeautifulSoup(response,  "html.parser")
    #print(soup.prettify())

    meta = OrderedDict()
    result_list = soup.find_all("result")

    for result in result_list:
        #print(result)
        result_title = get_xml_node_value(result, "title")

        if title_match(title, result_title):
            meta["doi"] = get_xml_node_value(result, "doi")
            meta["pmcid"] = get_xml_node_value(result, "pmcid")
            meta["journal"] = get_xml_node_value(result, "journaltitle")
            meta["authors"] = get_xml_node_value(result, "authorstring").split(", ")

            if get_xml_node_value(result, "haspdf") == "Y":
                meta["pdf"] = "http://europepmc.org/articles/{}?pdf=render".format(meta["pmcid"])

    return meta


######################################################################
## openAIRE

OPENAIRE_API_URL = "http://api.openaire.eu/search/publications?title={}"


def openaire_get_api_url (title):
    """
    construct a URL to query the API for OpenAIRE
    """
    return OPENAIRE_API_URL.format(urllib.parse.quote(title))


def openaire_title_search (title):
    """
    parse metadata from XML returned from the OpenAIRE API query
    """
    url = openaire_get_api_url(title)
    response = requests.get(url).text
    soup = BeautifulSoup(response,  "html.parser")
    #print(soup.prettify())

    meta = OrderedDict()

    for result in soup.find_all("oaf:result"):
        result_title = get_xml_node_value(result, "title")

        if title_match(title, result_title):
            meta["url"] = get_xml_node_value(result, "url")
            meta["authors"] = [a.text for a in result.find_all("creator")]
            meta["open"] = len(result.find_all("bestaccessright",  {"classid": "OPEN"})) > 0
            break

    return meta


######################################################################
## RePEc API

REPEC_CGI_URL = "https://ideas.repec.org/cgi-bin/htsearch?q={}"
REPEC_API_URL = "https://api.repec.org/call.cgi?code={}&getref={}"


def repec_get_cgi_url (title):
    """
    construct a URL to query the CGI for RePEc
    """
    enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))
    return REPEC_CGI_URL.format(enc_title)


def repec_get_api_url (handle, token):
    """
    construct a URL to query the API for RePEc
    """
    return REPEC_API_URL.format(token, handle)


def repec_get_handle (title):
    url = repec_get_cgi_url(title)
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


def repec_get_meta (token, handle):
    try:
        url = repec_get_api_url(token, handle)
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


def semantic_get_api_url (identifier):
    """
    construct a URL to query the API for Semantic Scholar
    """
    return SEMANTIC_API_URL.format(identifier)


def semantic_publication_lookup (identifier):
    """
    parse metadata returned from a Semantic Scholar API query
    """
    url = semantic_get_api_url(identifier)
    meta = requests.get(url).text
    return json.loads(meta)


######################################################################
## Unpaywall API

UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/{}?email={}"


def unpaywall_get_api_url (doi, email):
    """
    construct a URL to query the API for Unpaywall
    """
    return UNPAYWALL_API_URL.format(doi, email)


def unpaywall_publication_lookup (doi, email):
    """
    parse metadata returned from an Unpaywall API query
    """
    url = unpaywall_get_api_url(doi, email)
    meta = requests.get(url).text
    return json.loads(meta)


######################################################################
## main entry point (not used)

if __name__ == "__main__":
    print([ (k, v) for k, v in CONFIG["DEFAULT"].items()])
