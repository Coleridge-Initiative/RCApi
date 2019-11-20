
import unittest
# import configparser
# import dimensions_search_api_client as dscli
import urllib
import requests
from bs4 import BeautifulSoup
import RichContextApi_new
import importlib
importlib.reload(RichContextApi_new)



def oa_load_uri (uri):
    with urllib.request.urlopen(uri) as response:
        html = response.read()
        return html.decode("utf-8")
    

API_URI = "http://api.openaire.eu/search/publications?title="

def get_oa_metadata (title):
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
    
    


class TestVerifypublications (unittest.TestCase):
    
    def allow_arg(self):
        return None
    
    def setUp(self):
        """load titles to test APIs"""
        self.dimensions_title = 'Relationships between Diet, Alcohol Preference, and Heart Disease and Type 2 Diabetes among Americans'
        self.ssrn_title = 'Modeling the Term Structure from the On-the-Run Treasury Yield Curve'
        self.oa_title = "Categorizing US State Drinking Practices and Consumption Trends"
        self.epmc_url = "http://europepmc.org/abstract/MED/20195444"
    
    def test_dimensions(self):
        title = self.dimensions_title
        api_client = RichContextApi_new.connect_dimensions_api()
        dimensions_return = RichContextApi_new.dimensions_title_search(title,api_client)
        if dimensions_return:
            print('Dimensions API was pinged successfully')
        if not dimensions_return:
            print('Dimensions API failed')

   
    def test_epmc (self):
        url = self.epmc_url
        epmc_md = RichContextApi_new.get_europepmc_metadata(url)
        if epmc_md:
            print('new EuropePMC was pinged succesfully')
        if not epmc_md:
            print('EuropePMC failed')
        
    # def test_ssrn (self):
    #     ssrn_results = RichContextAPI.get_ssrn_md(self.ssrn_title)
    #     print('For title "{}", ssrn returned results: {}'.format(self.ssrn_title,ssrn_results))
    
    def test_oa (self):
        title = self.oa_title
        oa_d = oa_lookup_pub_uris(title)
        if oa_d:
            print('OpenAire was pinged succesfully')
        if not oa_d:
            print('OpenAire Failed')

if __name__ == "__main__":
    unittest.main()
