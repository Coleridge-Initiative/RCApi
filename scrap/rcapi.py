#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib import parse
import configparser
import json
import re
import requests
import sys
import time
import traceback
import urllib.parse
import urllib.request
import xml
import xml.etree.ElementTree as et

CONFIG_FILE = "richcontext_config.cfg"


###########################################################################################
## EuropePMC

def get_xml_node_value (root, name):
    """
    return the value from an XML node, if it exists
    """
    node = root.find(name)

    if node:
        return node.text
    else:
        return None


def title_match (title0, title1):
    """
    within reason, do the two titles match?
    """
    return title0 == title1


def europepmc_get_url (title):
    """
    construct a URL to query the API for EuropePMC
    """
    EUROPEPMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
    return EUROPEPMC_URL + urllib.parse.quote(title)


def europepmc_title_search (title):
    """
    parse metadata from XML returned from the EuropePMC API query
    """
    url = europepmc_get_url(title)
    response = requests.get(url).text
    soup = BeautifulSoup(response,  "html.parser")
    #print(soup)

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



def europepmc_url_search (url):
    """
    parse metadata from a Europe PMC web page for a publication
    """
    response = requests.get(url).text

    publisher = None
    doi = None
    pdf = None
    new_url = None

    soup = BeautifulSoup(response,  "html.parser")
    publisher_list_pmcmata = soup.find_all("span",  {"id": "pmcmata"})

    if len(publisher_list_pmcmata) > 0:
        for x in publisher_list_pmcmata:
            publisher = x.get_text()

    else:
        publisher_list_citation = soup.find_all("meta",  {"name": "citation_journal_abbrev"})

        if len(publisher_list_citation) > 0:
            for x in publisher_list_citation:
                publisher = x["content"]

    for x in soup.find_all("meta", {"name": "citation_doi"}):
        doi = x["content"]

    for x in soup.find_all("meta", {"name": "citation_pdf_url"}):
        pdf = x["content"]

    for x in soup.find_all("a", {"class": "abs_publisher_link"}):
        new_url = x["href"]

    if doi:
        epmc_data = {"doi":doi}
    if publisher:
        epmc_data.update({"journal":publisher})
    if pdf:
        epmc_data.update({"pdf":pdf})
    if new_url:
        epmc_data.update({"url":new_url})
        return epmc_data
    else:
        return None
    
    
def get_epmc_page (title):
    search_url = gen_empc_url(title)
    print(search_url)

    response = requests.get(search_url).text
    print(response)

    soup = BeautifulSoup(response,  "html.parser")
    all_results = soup.findAll("div",  {"itemtype": "http://schema.org/ScholarlyArticle"})

    for article in all_results:
        this_title = article.find("a", {"resultLink linkToAbstract"}).text.rstrip(".\n").lower()
        my_title = title.lower()

        if my_title == this_title:
            article_open_url_search = article.find(
                "div",
                {"abs_link_metadata pmid_free_text_information"}
                ).find("span", {"freeResource"})

            if article_open_url_search is not None:
                article_url = article_open_url_search.find("a", {"resultLink linkToFulltext"})
            else:
                article_url = article.find("a", {"resultLink linkToAbstract"})

            article_url_final = "http://europepmc.org" + article_url["href"].split(";")[0].lstrip(".")
            article_data = {"url":article_url_final, "title":this_title}
            return article_data

        else:
            return None
    

def get_epmc_md (title):
    page_md = get_epmc_page(title)

    if page_md is not None:
        epmc_md = get_europepmc_metadata(page_md["url"])
        epmc_md.update(page_md)
        return epmc_md

    else:
        return None


###########################################################################################
## Dimensions API


def gen_dimensions_token():
#     CONFIG_FILE = "rc.cfg"
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CONFIG_FILE)
    username = CONFIG.get('DEFAULT',  'username')
    password = CONFIG.get('DEFAULT',  'password')
    login = {
    'username': username,
    'password': password
    }
    resp = requests.post('https://app.dimensions.ai/api/auth.json', json=login)
    if resp.raise_for_status() is not None:
        print('Check credentials or permissions.')
    header = {
    'Authorization': "JWT " + resp.json()['token']}
    return header
        
    
def run_dimensions_query(query):
    header = gen_dimensions_token()
    resp = requests.post(
    'https://app.dimensions.ai/api/dsl.json',
    data= query.encode(),
    headers=header)

    response = resp.json()
    return response
    
def dimensions_title_search (title):
    title =  title.replace('"', '\\"')
    title_query = 'search publications in title_only for "\\"{}\\"" return publications[all]'.format(title)
    dimensions_return = run_dimensions_query(query=title_query)

    try:
        title_return = dimensions_return["publications"]
        try:
            [p.update({'journal':p['journal']['title']}) for p in title_return]
        except:
            pass
        if len(title_return) > 0:
            return title_return
        else:
            return None
    except:
        pass
        #print("error with title {}".format(title))


def dimensions_fulltext_search(search_term):
    search_string = 'search publications in full_data for "\\"{}\\"" return publications[doi+title+journal]'.format(search_term)
    api_response = run_dimensions_query(query = search_string )
    publication_data = api_response['publications']
    try:
        [p.update({'journal':p['journal']['title']}) for p in publication_data]
    except:
        pass
    return publication_data

###########################################################################################
####################################  SSRN   #############################################
###########################################################################################

def get_author(soup):
    author_chunk = soup.find(class_ = "authors authors-full-width")
    author_chunk.find_all(['a',  'p'])
    filtered_list = [e for e in author_chunk.find_all(['a',  'p']) if len(e.contents) == 1]
    n = 2
    nested_list = [filtered_list[i * n:(i + 1) * n] for i in range((len(filtered_list) + n - 1) // n )]  
    auth_list = []
    for i in nested_list:
        auth = i[0].text
        affl = i[1].text
        auth_dict = {"author_name":auth, "affl":affl}
        auth_list.append(auth_dict)
    return(auth_list)

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text,  'html.parser')
    return soup

def get_ssrn_metadata(url):
    soup = get_soup(url)
    
    pub_title = soup.find("meta",  attrs={'name':'citation_title'})

    title = pub_title['content']

    keywords_list_raw = soup.find("meta",  attrs={'name':'citation_keywords'})['content'].split(', ')
    keywords = [k.strip() for k in keywords_list_raw]

    doi = soup.find("meta",   {"name": "citation_doi"})["content"]
    
    authors = get_author(soup)
    
    pub_dict = {'title':title, 'keywords':keywords, 'doi':doi,  'authors':authors,  'url':url}
    return pub_dict

def ssrn_url_search(pub):
    url = pub['url']
    doi = pub['doi']
    if 'ssrn' in url:
        pub_dict = get_metadata(url)
    elif 'ssrn' not in url:
        if 'ssrn' in doi:
            doi = doi.split('ssrn.', 1)[1]
            url = 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=' + doi
            pub_dict = get_metadata(url)
            return pub_dict
        elif 'ssrn' not in doi:
            return []
        
        
def search_ssrn(title):
    ssrn_homepage = 'https://www.ssrn.com/index.cfm/en/'
    CONFIG = configparser.ConfigParser()
    CONFIG.read(CONFIG_FILE)
    chrome_path = CONFIG.get('DEFAULT',  'chrome_exe_path')
    browser = webdriver.Chrome(executable_path=chrome_path)
    # browser = webdriver.Chrome(executable_path="/Users/sophierand/RCApi/chromedriver.exe")
    browser.get(ssrn_homepage)
    class_name = 'form-control'
    search = browser.find_element_by_class_name(class_name)
    search.send_keys(title)
    search.send_keys(Keys.RETURN)
    search_url = browser.current_url
    search_url_result = browser.get(search_url)
    result_element = browser.find_element_by_xpath("//*[@class='title optClickTitle']")
    ssrn_link = result_element.get_attribute('href')
    browser.quit()
    return ssrn_link


def get_ssrn_md(title):
    ssrn_article_url = search_ssrn(title)
    ssrn_metadata = get_ssrn_metadata(ssrn_article_url)
    return ssrn_metadata


###########################################################################################
###############################     openAIRE     ##########################################
###########################################################################################
def oa_fulltext_search(search_term):
    search_term_format = re.sub(" ","+",search_term)
    search_url = 'https://explore.openaire.eu/search/find?keyword=%22{}%22'.format(search_term_format)
    response = requests.get(search_url).text
    soup = BeautifulSoup(response, "html.parser")
    titles = soup.find_all("div",  {"class": "uk-h5"})
    pub_list = []
    for t in titles:
        pub_dict = {}
        title_text = t.text
        oa_title_return = oa_title_search(title_text)
        if oa_title_return:
            pub_list.append(oa_title_return)
    return pub_list


def oa_url_search(url):
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    data = soup.select("[type='application/ld+json']")[0]
    pub_dict = {'url':url,'title':json.loads(data.text)["name"]}
    try:
        if json.loads(data.text)["identifier"]['propertyID'] == 'doi':
            doi = json.loads(data.text)["identifier"]["value"]
            pub_dict.update({'doi':json.loads(data.text)["identifier"]["value"]})
        else:
            pass
    except:
        pass
    return pub_dict



def oa_load_uri (uri):
    with urllib.request.urlopen(uri) as response:
        html = response.read()
        return html.decode("utf-8")
    

API_URI = "http://api.openaire.eu/search/publications?title="

def oa_title_search (title):
    xml = oa_load_uri(API_URI + parse.quote(title))
    pub_url = oa_extract_pub_uri(xml)
    journal = oa_extract_journal(xml)
    doi = oa_extract_doi(xml)

    if pub_url:
        oa_dict = {'journal':journal, 'title':title, 'doi':doi}
        oa_dict.update(pub_url)
        return oa_dict
    if not pub_url:
        return None


NS = {
    "oaf": "http://namespace.openaire.eu/oaf"
    }

def oa_extract_pub_uri (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result",  NS)

    if len(result) > 0:
        url_list = result[0].findall("./children/instance/webresource/url")

        if len(url_list) > 0:
            url_list_text = [u.text for u in url_list]
            pdf = [p for p in url_list_text if 'pdf' in p]
            url = [u for u in url_list_text if u not in pdf and 'europepmc' in u]
            url_dict = {}
            if len(url) > 0:
                url_dict.update({'url':url[0]})
            if len(pdf) > 0:
                url_dict.update({'pdf':pdf[0]})

#             pub_url = url_list[0].text
            return url_dict

    return None

def oa_extract_publisher (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result",  NS)
    if len(result) > 0:
        publisher_list = result[0].findall("./collectedfrom")
        if len(publisher_list) > 0:
            publisher_name = publisher_list[0].attrib['name']
            return publisher_name
    elif len(result) == 0:
        return None
    
    
def oa_extract_doi (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result",  NS)
    if len(result) > 0:
        doi = result[0].find("./pid[@classid='doi']")
        if doi is not None:
            doi = doi.text
            return doi

def oa_extract_journal (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result",  NS)
    if len(result) > 0:
        journal = result[0].find("./journal")
        if journal is not None:
            journal_name = journal.text
            return journal_name

###########################################################################################
############################  Consolidated Functions   ####################################
###########################################################################################

def url_search(url,api_name):
    if api_name.lower() == "europepmc":
        url_search_result = epmc_url_search(url)
    if api_name.lower() == "openaire":
        url_search_result = oa_url_search(url)
               
def fulltext_search(search_term,api_name):
    if api_name.lower() == "dimensions":
        api_client = connect_dimensions_api()
        fulltext_result = dimensions_fulltext_search(search_term = search_term,api_client = api_client)        
    if api_name.lower() in ['researchgate','research gate']:
        fulltext_result = rg_fulltext_search(search_term = search_term)
    if api_name.lower() == 'openaire':
        fulltext_result = oa_fulltext_search(search_term = search_term)
    return fulltext_result
    
def title_search(title, api_name):
    if api_name.lower() == 'dimensions':
        titlesearch_result = dimensions_title_search(title)
        
    if api_name.lower() == 'ssrn':
        titlesearch_result = search_ssrn(title)

    if api_name.lower() == 'europepmc':
        titlesearch_result = get_epmc_page(title)
    
    if api_name.lower() == 'openaire':
        titlesearch_result = oa_title_search(title)
        
    return titlesearch_result


######################################################################
## main entry point

if __name__ == "__main__":

    title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."

    results = europepmc_title_search(title)
    print(results)
