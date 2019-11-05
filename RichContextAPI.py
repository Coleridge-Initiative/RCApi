import dimensions_search_api_client as dscli
import configparser
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
import requests
import time
import urllib.request
from urllib import parse
import xml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import json
import re
import sys
import traceback
import urllib.parse

###########################################################################################
################################   DIMENSIONS    ##########################################
###########################################################################################
def connect_ds_api(username,password):
    api_client = dscli.DimensionsSearchAPIClient()
    api_client.set_max_in_items( 100 )
    api_client.set_max_return( 1000 )
    api_client.set_max_overall_returns( 50000 )
    api_client.set_username( username )
    api_client.set_password( password )
    return api_client


def search_title(title,api_client):
    title =  title.replace('"','\\"')
    query = 'search publications in title_only for "\\"{}\\"" return publications[all]'.format(title)
    dimensions_return = api_client.execute_query(query_string_IN = query )
    try:
        title_return = dimensions_return['publications']
        if len(title_return) > 0:
            return title_return
        else:

            return None
    except:
        pass
#         print('error with title {}'.format(title))
        
def run_pub_id_search(dimensions_id,api_client):
    id_search_string = 'search publications where id = "{}" return publications[all] limit 1'.format(dimensions_id)
    id_response = api_client.execute_query( query_string_IN=id_search_string )
    publication_metadata = id_response['publications'][0]
    return publication_metadata


def format_dimensions(dimensions_md):
    filt_keys = list(set(list(dimensions_md.keys())) & set(['authors','doi','linkout','concepts', 'terms','journal']))
    pubs_dict = {k:dimensions_md[k] for k in filt_keys}
    pubs_dict['keywords'] = list(set(pubs_dict['terms'] + pubs_dict['concepts']))
    pubs_dict['journal_title'] = pubs_dict['journal']['title']
    final_keys = list(set(filt_keys) & set(['authors','doi','linkout','keywords','journal_title'])) + ['keywords', 'journal_title']
    pubs_dict_final = {k:pubs_dict[k] for k in final_keys}
    return pubs_dict_final

def dimensions_run_exact_string_search(string,api_client):
    search_string = 'search publications in full_data for "\\"{}\\"" return publications[doi+title+journal+author_affiliations]'.format(string)
    api_response = api_client.execute_query(query_string_IN = search_string )
    return api_response

def dimensions_from_title(title,api_client):
#     title = pub_entry['title']
    dimensions_md_all = search_title(title = title, api_client = api_client)
    if dimensions_md_all:
        dimensions_md = dimensions_md_all[0]
        dimensions_pubs_dict = format_dimensions(dimensions_md)
        dimensions_pubs_dict.update({'title':title})
#     pub_entry.update({'dimensions':dimensions_pubs_dict})
        return dimensions_pubs_dict

def connect_dimensions_api():
    CONFIG = configparser.ConfigParser()
    CONFIG.read("richcontext_config.cfg")
    api_client = connect_ds_api(username= CONFIG.get('DEFAULT','username'),password = CONFIG.get('DEFAULT','password'))
    return api_client

def dimensions_title_search(title,api_client):
    pub_dict = dimensions_from_title(title = title,api_client = api_client)
    return pub_dict


def get_dimensions_md(title):
    api_cnxn = connect_dimensions_api()
    dimensions_md = dimensions_title_search(title,api_cnxn)
    return dimensions_md



###########################################################################################
####################################  SSRN   #############################################
###########################################################################################

def get_author(soup):
    author_chunk = soup.find(class_ = "authors authors-full-width")
    author_chunk.find_all(['a', 'p'])
    filtered_list = [e for e in author_chunk.find_all(['a', 'p']) if len(e.contents) == 1]
    n = 2
    nested_list = [filtered_list[i * n:(i + 1) * n] for i in range((len(filtered_list) + n - 1) // n )]  
    auth_list = []
    for i in nested_list:
        auth = i[0].text
        affl = i[1].text
        auth_dict = {"author_name":auth,"affl":affl}
        auth_list.append(auth_dict)
    return(auth_list)

def get_soup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_ssrn_metadata(url):
    soup = get_soup(url)
    
    pub_title = soup.find("meta", attrs={'name':'citation_title'})

    title = pub_title['content']

    keywords_list_raw = soup.find("meta", attrs={'name':'citation_keywords'})['content'].split(',')
    keywords = [k.strip() for k in keywords_list_raw]

    doi = soup.find("meta",  {"name": "citation_doi"})["content"]
    
    authors = get_author(soup)
    
    pub_dict = {'title':title,'keywords':keywords,'doi':doi, 'authors':authors, 'url':url}
    return pub_dict

def ssrn_url_search(pub):
    url = pub['url']
    doi = pub['doi']
    if 'ssrn' in url:
        pub_dict = get_metadata(url)
    elif 'ssrn' not in url:
        if 'ssrn' in doi:
            doi = doi.split('ssrn.',1)[1]
            url = 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=' + doi
            pub_dict = get_metadata(url)
            return pub_dict
        elif 'ssrn' not in doi:
            return []
        
        
def search_ssrn(title):
    ssrn_homepage = 'https://www.ssrn.com/index.cfm/en/'
    CONFIG = configparser.ConfigParser()
    CONFIG.read("api_config.cfg")
    chrome_path = CONFIG.get('DEFAULT','chrome_exe_path')
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
###############################     EuropePMC     #########################################
###########################################################################################




def flatten(l):
    sl = [item for sublist in l for item in sublist]
    return sl
def gen_empc_url(title):
    epmc_url = 'http://europepmc.org/search?query=' + urllib.parse.quote(title)
    return epmc_url

def get_europepmc_metadata (url):
    """
    parse metadata from a Europe PMC web page for a publication
    """

    response = requests.get(url).text

    publisher = None
    doi = None
    pdf = None
    new_url = None

    soup = BeautifulSoup(response, "html.parser")


    publisher_list_pmcmata = soup.find_all("span", {"id": "pmcmata"})
    if len(publisher_list_pmcmata) > 0:
        for x in publisher_list_pmcmata:
            publisher = x.get_text()
    if len(publisher_list_pmcmata) == 0:
        publisher_list_citation = soup.find_all("meta", {"name": "citation_journal_abbrev"})
        if len(publisher_list_citation) > 0:
            for x in publisher_list_citation:
                publisher = x['content']

    for x in soup.find_all("meta",  {"name": "citation_doi"}):
        doi = x["content"]

    for x in soup.find_all("meta",  {"name": "citation_pdf_url"}):
        pdf = x["content"]

    for x in soup.find_all("a",  {"class": "abs_publisher_link"}):
        new_url = x['href']

    if doi:
        epmc_data = {'doi':doi}
    if publisher:
        epmc_data.update({'journal':publisher})
    if pdf:
        epmc_data.update({'pdf':pdf})
    if new_url:
        epmc_data.update({'url':new_url})
        return epmc_data
    else:
        return None
    
    
def get_epmc_page(title):
    search_url = gen_empc_url(title)
    response = requests.get(search_url).text
    soup = BeautifulSoup(response, "html.parser")
    all_results = soup.findAll("div", {"itemtype": "http://schema.org/ScholarlyArticle"})
    for article in all_results:
        this_title = article.find('a',{'resultLink linkToAbstract'}).text.rstrip('.\n').lower()
        my_title = title.lower()
        if my_title == this_title:
            article_open_url_search =  article.find('div',{'abs_link_metadata pmid_free_text_information'}).find('span',{'freeResource'})
            if article_open_url_search is not None:
                article_url = article_open_url_search.find('a',{'resultLink linkToFulltext'})
            if article_open_url_search is None:
                article_url = article.find('a',{'resultLink linkToAbstract'})
            article_url_final = 'http://europepmc.org' + article_url['href'].split(';')[0].lstrip('.')
            article_data = {'url':article_url_final,'title':this_title}
            return article_data
        if my_title != this_title:
            return None
    

def get_epmc_md(title):
    page_md = get_epmc_page(title)
    if page_md is not None:
        epmc_md = get_europepmc_metadata(page_md['url'])
        epmc_md.update(page_md)
        return epmc_md
    if page_md is None:
        return None






###########################################################################################
###############################     openAIRE     ##########################################
###########################################################################################





def oa_load_uri (uri):
    with urllib.request.urlopen(uri) as response:
        html = response.read()
        return html.decode("utf-8")
    

API_URI = "http://api.openaire.eu/search/publications?title="

def oa_lookup_pub_uris (title):
    xml = oa_load_uri(API_URI + parse.quote(title))
    pub_url = oa_extract_pub_uri(xml)
    journal = oa_extract_journal(xml)
    doi = oa_extract_doi(xml)

    if pub_url:
        oa_dict = {'journal':journal,'title':title,'doi':doi}
        oa_dict.update(pub_url)
        return oa_dict
    if not pub_url:
        return None



NS = {
    "oaf": "http://namespace.openaire.eu/oaf"
    }

def oa_extract_pub_uri (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result", NS)

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
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result", NS)
    if len(result) > 0:
        publisher_list = result[0].findall("./collectedfrom")
        if len(publisher_list) > 0:
            publisher_name = publisher_list[0].attrib['name']
            return publisher_name
    elif len(result) == 0:
        return None
    
    
def oa_extract_doi (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result", NS)
    if len(result) > 0:
        doi = result[0].find("./pid[@classid='doi']")
        if doi is not None:
            doi = doi.text
            return doi

def oa_extract_journal (xml):
    root = et.fromstring(xml)
    result = root.findall("./results/result[1]/metadata/oaf:entity/oaf:result", NS)
    if len(result) > 0:
        journal = result[0].find("./journal")
        if journal is not None:
            journal_name = journal.text
            return journal_name



def full_text_search(search_term, api_name):