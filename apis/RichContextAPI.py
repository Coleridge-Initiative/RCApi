#Dimensions
import dimensions_search_api_client as dscli
import configparser

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
        print('error with title {}'.format(title))
        
def run_pub_id_search(dimensions_id,api_client):
    id_search_string = 'search publications where id = "{}" return publications[all] limit 1'.format(dimensions_id)
    id_response = api_client.execute_query( query_string_IN=id_search_string )
    publication_metadata = id_response['publications'][0]
    return publication_metadata


def format_dimensions(dimensions_md):
    pubs_dict = {k:dimensions_md[k] for k in ['authors','doi','linkout','concepts', 'terms','journal']}
    pubs_dict['keywords'] = list(set(pubs_dict['terms'] + pubs_dict['concepts']))
    pubs_dict['journal_title'] = pubs_dict['journal']['title']
    pubs_dict_final = {k:pubs_dict[k] for k in ['authors','doi','linkout','keywords','journal_title']}
    return pubs_dict_final


def dimensions_from_title(pub_entry,api_client):
    title = pub_entry['title']
    dimensions_md_all = search_title(title = title, api_client = api_client)
    dimensions_md = dimensions_md_all[0]
    dimensions_pubs_dict = format_dimensions(dimensions_md)
    pub_entry.update({'dimensions':dimensions_pubs_dict})
    return pub_entry

def dimensions_main(pub):
    CONFIG = configparser.ConfigParser()
    CONFIG.read("dimensions.cfg")
    api_client = connect_ds_api(username= CONFIG.get('DEFAULT','username'),password = CONFIG.get('DEFAULT','password'))
    pub_dict = dimensions_from_title(pub_entry = pub,api_client = api_client)
    return pub_dict


#RePEc

#  repec_token = CONFIG["DEFAULT"]["repec_token"]


# SSRN
from bs4 import BeautifulSoup
import requests
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

def get_metadata(url):
    soup = get_soup(url)
    
    pub_title = soup.find("meta", attrs={'name':'citation_title'})

    title = pub_title['content']

    keywords_list_raw = soup.find("meta", attrs={'name':'citation_keywords'})['content'].split(',')
    keywords = [k.strip() for k in keywords_list_raw]

    doi = soup.find("meta",  {"name": "citation_doi"})["content"]
    
    authors = get_author(soup)
    
    pub_dict = {'title':title,'keywords':keywords,'doi':doi, 'authors':authors, 'url':url}
    return pub_dict

def ssrn_main(pub):
    url = pub['url']
    if 'ssrn' not in url:
        doi = pub['doi'].split('ssrn.',1)[1]
        url = 'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=' + doi
    pub_dict = get_metadata(url)
    return pub_dict