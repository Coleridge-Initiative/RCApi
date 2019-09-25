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


# ####

def dimensions_main(pub):
    CONFIG = configparser.ConfigParser()
    CONFIG.read("dimensions.cfg")
    api_client = connect_ds_api(username= CONFIG.get('DEFAULT','username'),password = CONFIG.get('DEFAULT','password'))
    pub_dict = dimensions_from_title(pub_entry = pub,api_client = api_client)
    return pub_dict