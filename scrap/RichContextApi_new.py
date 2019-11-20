import configparser
import dimensions_search_api_client as dscli
import urllib
import requests
from urllib import parse
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup


###########################################################################################
################################   DIMENSIONS    ##########################################
###########################################################################################


def connect_dimensions_api():
    CONFIG = configparser.ConfigParser()
    CONFIG.read("richcontext_config.cfg")
    api_client = dscli.DimensionsSearchAPIClient()
    username = CONFIG.get('DEFAULT','username')
    password = CONFIG.get('DEFAULT','password')
    api_client.set_username( username )
    api_client.set_password( password )
    return api_client


################################   title search    #####################################

def dimensions_title_search(title,api_client):
    title_query = 'search publications in title_only for "\\"{}\\"" return publications[all]'.format(title)
    dimensions_return = api_client.execute_query(query_string_IN = title_query)
    dimensions_title_return = dimensions_return['publications']
    return dimensions_title_return

##########################   full text string search    ###########################
def dimensions_fulltext_search(search_term,api_client):
    search_string = 'search publications in full_data for "\\"{}\\"" return publications[doi+title+journal]'.format(search_term)
    api_response = api_client.execute_query(query_string_IN = search_string )
    publication_data = api_response['publications']
    [p.update({'journal':p['journal']['title']}) for p in publication_data]
    return publication_data

###########################################################################################
################################   EuropePMC    ##########################################
###########################################################################################

################################   page url search    #####################################
def get_europepmc_metadata (url):
    """
    parse metadata from a Europe PMC web page for a publication
    example url: http://europepmc.org/abstract/MED/20195444

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
    for x in soup.find_all("meta",  {"name": "citation_title"}):
        title = x['content']

    for x in soup.find_all("meta",  {"name": "citation_doi"}):
        doi = x["content"]

    for x in soup.find_all("meta",  {"name": "citation_pdf_url"}):
        pdf = x["content"]

    for x in soup.find_all("a",  {"class": "abs_publisher_link"}):
        new_url = x['href']

    if title:
        epmc_data = {'title':title}
    if doi:
        epmc_data.update({'doi':doi})
    if publisher:
        epmc_data.update({'journal':publisher})
    if pdf:
        epmc_data.update({'pdf':pdf})
    if new_url:
        epmc_data.update({'url':new_url})
        return epmc_data
    else:
        return None


###########################################################################################
##########################       ResearchGate functions    ###############################
###########################################################################################

##########################   full text string search    ###########################
    
def rg_query(search_term):
    pub_list = []
    search_term_format = re.sub(" ","+",search_term)
    search_url = 'https://www.researchgate.net/search/publication?q=%22{}%22'.format(search_term_format)

    response = requests.get(search_url).text
    soup = BeautifulSoup(response, "html.parser")

    titles = soup.find_all("div",  {"itemtype": "http://schema.org/ScholarlyArticle"})
    for t in titles:
        pub_dict = {}
        a = t.find_all("a",{"class":"nova-e-link nova-e-link--color-inherit nova-e-link--theme-bare"})[0]
        title = a.text
        url = "https://www.researchgate.net/"+a['href']
        l = t.find_all("li",{"class":"nova-e-list__item nova-v-publication-item__meta-data-item"})
        pub_dict = {'title':title,'url':url}
        try:
            doi = [re.sub("DOI:"," ",d.text).rstrip().lstrip() for d in l if 'DOI' in d.text][0]
            pub_dict.update({'doi':doi})
        except:
            pass
        pub_list.append(pub_dict)
    return pub_list  


###########################################################################################
##########################       Consolidation functions    ###############################
###########################################################################################


def title_search(title, api_name):
    if api_name.lower() == 'dimensions':
        titlesearch_result = dimensions_title_search(title)


def url_search(url,api_name):
    if api_name.lower() == "europepmc":
        url_search_result = get_europepmc_metadata(url)
        
def fulltext_search(search_term,api_name):
    if api_name.lower() == "dimensions":
        api_client = connect_dimensions_api()
        fulltext_result = dimensions_fulltext_search(search_term = search_term,api_client = api_client)        
    if api_name.lower() in ['researchgate','research gate']:
        fulltext_result = rg_query(search_term = search_term)
    


