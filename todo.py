#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import configparser
import dimensions_search_api_client as dscli
import json
import re
import requests
import sys
import time
import traceback
import urllib.parse
import urllib.request


CONFIG_FILE = "rc.cfg"

CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_FILE)


######################################################################
## Dimensions API

def connect_ds_api (username, password):
    api_client = dscli.DimensionsSearchAPIClient()
    api_client.set_max_in_items(100)
    api_client.set_max_return(1000)
    api_client.set_max_overall_returns(50000)
    api_client.set_username(username)
    api_client.set_password(password)
    return api_client


def search_title (title, api_client):
    title =  title.replace('"', '\\"')
    query = 'search publications in title_only for "\\"{}\\"" return publications[all]'.format(title)
    dimensions_return = api_client.execute_query(query_string_IN=query)

    try:
        title_return = dimensions_return["publications"]

        if len(title_return) > 0:
            return title_return
        else:
            return None
    except:
        pass
        #print("error with title {}".format(title))


def run_pub_id_search(dimensions_id,api_client):
    id_search_string = 'search publications where id = "{}" return publications[all] limit 1'.format(dimensions_id)
    id_response = api_client.execute_query( query_string_IN=id_search_string )
    publication_metadata = id_response["publications"][0]
    return publication_metadata


def format_dimensions(dimensions_md):
    filt_keys = list(set(list(dimensions_md.keys())) & set(["authors", "doi", "linkout", "concepts",  "terms", "journal"]))
    pubs_dict = {k:dimensions_md[k] for k in filt_keys}
    pubs_dict["keywords"] = list(set(pubs_dict["terms"] + pubs_dict["concepts"]))
    pubs_dict["journal_title"] = pubs_dict["journal"]["title"]
    final_keys = list(set(filt_keys) & set(["authors", "doi", "linkout", "keywords", "journal_title"])) + ["keywords",  "journal_title"]
    pubs_dict_final = {k:pubs_dict[k] for k in final_keys}
    return pubs_dict_final

def dimensions_run_exact_string_search(string, api_client):
    search_string = 'search publications in full_data for "\\"{}\\"" return publications[doi+title+journal+author_affiliations]'.format(string)
    api_response = api_client.execute_query(query_string_IN = search_string )
    return api_response

def dimensions_from_title(title, api_client):
#     title = pub_entry["title"]
    dimensions_md_all = search_title(title = title,  api_client = api_client)
    if dimensions_md_all:
        dimensions_md = dimensions_md_all[0]
        dimensions_pubs_dict = format_dimensions(dimensions_md)
        dimensions_pubs_dict.update({"title":title})
#     pub_entry.update({"dimensions":dimensions_pubs_dict})
        return dimensions_pubs_dict

def connect_dimensions_api():
    username = CONFIG["DEFAULT"]["email"]
    password = CONFIG["DEFAULT"]["dimensions_password"]
    api_client = connect_ds_api(username, password)
    return api_client

def dimensions_title_search(title, api_client):
    pub_dict = dimensions_from_title(title = title, api_client = api_client)
    return pub_dict


def get_dimensions_md(title):
    api_cnxn = connect_dimensions_api()
    dimensions_md = dimensions_title_search(title, api_cnxn)
    return dimensions_md


######################################################################
## SSRN

def get_author(soup):
    author_chunk = soup.find(class_ = "authors authors-full-width")
    author_chunk.find_all(["a",  "p"])
    filtered_list = [e for e in author_chunk.find_all(["a",  "p"]) if len(e.contents) == 1]
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
    soup = BeautifulSoup(response.text,  "html.parser")
    return soup

def get_ssrn_metadata(url):
    soup = get_soup(url)
    
    pub_title = soup.find("meta",  attrs={"name":"citation_title"})

    title = pub_title["content"]

    keywords_list_raw = soup.find("meta",  attrs={"name":"citation_keywords"})["content"].split(", ")
    keywords = [k.strip() for k in keywords_list_raw]

    doi = soup.find("meta",   {"name": "citation_doi"})["content"]
    
    authors = get_author(soup)
    
    pub_dict = {"title":title, "keywords":keywords, "doi":doi,  "authors":authors,  "url":url}
    return pub_dict

def ssrn_url_search(pub):
    url = pub["url"]
    doi = pub["doi"]
    if "ssrn" in url:
        pub_dict = get_metadata(url)
    elif "ssrn" not in url:
        if "ssrn" in doi:
            doi = doi.split("ssrn.", 1)[1]
            url = "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=" + doi
            pub_dict = get_metadata(url)
            return pub_dict
        elif "ssrn" not in doi:
            return []
        
        
def search_ssrn(title):
    ssrn_homepage = "https://www.ssrn.com/index.cfm/en/"
    chrome_path = CONFIG["DEFAULT"]["chrome_exe_path"]
    browser = webdriver.Chrome(executable_path=chrome_path)
    # browser = webdriver.Chrome(executable_path="/Users/sophierand/RCApi/chromedriver.exe")

    browser.get(ssrn_homepage)
    class_name = "form-control"

    search = browser.find_element_by_class_name(class_name)
    search.send_keys(title)
    search.send_keys(Keys.RETURN)

    search_url = browser.current_url
    search_url_result = browser.get(search_url)
    result_element = browser.find_element_by_xpath("//*[@class='title optClickTitle']")
    ssrn_link = result_element.get_attribute("href")
    browser.quit()

    return ssrn_link


def get_ssrn_md(title):
    ssrn_article_url = search_ssrn(title)
    ssrn_metadata = get_ssrn_metadata(ssrn_article_url)
    return ssrn_metadata


###########################################################################################
############################  Consolidated Functions   ####################################
###########################################################################################


def full_text_search(search_term, api_name):
    if api_name.lower() == "dimensions":
        api_client = connect_dimensions_api()
        stringsearch_result =  dimensions_run_exact_string_search(string=search_term, api_client=api_client)

        if stringsearch_result:
            ss_result = stringsearch_result["publications"]
    return ss_result


def title_search(title, api_name):
    if api_name.lower() == "dimensions":
        titlesearch_result = get_dimensions_md(title)
        
    if api_name.lower() == "ssrn":
        titlesearch_result = search_ssrn(title)

    if api_name.lower() == "europepmc":
        titlesearch_result = get_epmc_page(title)
    
    if api_name.lower() == "openaire":
        titlesearch_result = oa_lookup_pub_uris(title)
        
    return titlesearch_result


######################################################################
## main entry point

if __name__ == "__main__":

    doi = "10.1016/j.appet.2017.07.006"
    email = CONFIG["DEFAULT"]["email"]

    sys.exit(0)
