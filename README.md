# richcontext.scholapi

[Rich Context](https://coleridgeinitiative.org/richcontext)
API integrations for federating discovery services and metadata
exchange across multiple scholarly infrastructure providers.

Development of the Rich Context knowledge graph uses this library to:

  * identify dataset links to research publications
  * locate open access publications
  * reconcile journal references
  * reconcile author profiles
  * reconcile keyword taxonomy

This library has been guided by collaborative work on community
building and metadata exchange to improve Scholarly Infrastructure,
held at the *2019 Rich Context Workshop*.


## Installation

Prerequisites:

- [Python 3.x](https://www.python.org/downloads/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Biopython.Entrez](https://biopython.org/)
- [Crossref Commons](https://gitlab.com/crossref/crossref_commons_py)
- [Dimensions CLI](https://github.com/digital-science/dimcli)
- [Requests](https://2.python-requests.org/en/master/)
- [Requests-Cache](https://github.com/reclosedev/requests-cache)
- [Selenium](https://github.com/SeleniumHQ/selenium/)
- [xmltodict](https://github.com/martinblech/xmltodict)


To install from [PyPi](https://pypi.python.org/pypi/richcontext.scholapi):

```
pip install richcontext.scholapi
```

If you install directly from this Git repo, be sure to install the 
dependencies as well:

```
pip install -r requirements.txt
```

Then copy the configuration file template `rc_template.cfg` to `rc.cfg`
and populate it with your credentials.

NB: be careful not to commit the `rc.cfg` file in Git since by
definition it will contain sensitive data, e.g., your passwords.


Parameters used in the configuration file include:

| parameter | value | 
| --- | --- |
| `chrome_exe_path` | path/to/chrome.exe |
| `core_api_key` | CORE API key |
| `dimensions_password` | Dimensions API password |
| `elsevier_api_key` | Elsvier API key |
| `email` | personal email address |
| `orcid_secret` | ORCID API key |
| `repec_token` | RePEc API token |

Download the [Chrome webdriver](https://chromedriver.chromium.org/downloads) 
to enable use of Selenium (SSRN only).

For a good (although slightly dated) tutorial for installing and
testing Selenium on Ubuntu Linux, see:
<https://christopher.su/2015/selenium-chromedriver-ubuntu/>


## Usage

```
from richcontext import scholapi as rc_scholapi

# initialize the federated API access
schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg", logger=None)
source = schol.openaire

# search parameters for example publications
title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."

# run it...
meta, timing, message = source.title_search(title)

# report results
if message:
    # error case
    print(message)
else:
    print(meta)
    source.report_perf(timing)
```


## API Integrations

APIs used to retrieve metadata:

  * *PubMed family*
    + [PubMed](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
    + [EuropePMC](https://europepmc.org/RestfulWebService)

  * *Scholix family*
    + [OpenAIRE](https://develop.openaire.eu/)
    + [Crossref](https://www.crossref.org/services/metadata-delivery/)
    + [DataCite](https://support.datacite.org/docs/api)

  * *OA family*
    + [Unpaywall](https://unpaywall.org/products/api)
    + [dissemin](https://dissemin.readthedocs.io/en/latest/api.html)
    + [Semantic Scholar](http://api.semanticscholar.org/)

  * *Misc.*
    + [RePEc](https://ideas.repec.org/api.html)
    + [Dimensions](https://docs.dimensions.ai/dsl/api.html)
    + [SSRN](https://www.ssrn.com/)

See the coding examples in the `test.py` unit test for usage patterns
per supported API.


## Literature

For more background about *open access publications* see:

> Piwowar H, Priem J, Larivière V, Alperin JP, Matthias L, Norlander B, Farley A, West J, Haustein S. 2017.  
The State of OA: A large-scale analysis of the prevalence and impact of Open Access articles  
*PeerJ Preprints* 5:e3119v1  
<https://doi.org/10.7287/peerj.preprints.3119v1>


## Testing

First, be sure that you're testing the source and not from an
installed library.

Then run unit tests on the APIs for which you have credentials:

```
python test.py
```


## Contributions

If you'd like to contribute, please see our listings of
[*good first issues*](https://github.com/Coleridge-Initiative/RCApi/labels/good%20first%20issue).

For info about joining the AI team working on Rich Context, see
<https://github.com/Coleridge-Initiative/RCGraph/blob/master/SKILLS.md>


## Kudos

Contributors:
[@ceteri](https://github.com/ceteri), 
[@IanMulvany](https://github.com/IanMulvany),
[@srand525](https://github.com/srand525), 
[@ernestogimeno](https://github.com/ernestogimeno),
[@lobodemonte](https://github.com/lobodemonte),
plus many thanks for the inspiring *2019 Rich Context Workshop* notes by 
[@metasj](https://github.com/metasj),
and guidance from
[@claytonrsh](https://github.com/claytonrsh),
[@Juliaingridlane](https://github.com/Juliaingridlane).
