# richcontext.scholapi

[Rich Context](https://coleridgeinitiative.org/richcontext)
API integrations for federating metadata discovery and exchange across
multiple scholarly infrastructure providers.

Development of the Rich Context knowledge graph uses this library to:

  * identify dataset links to research publications
  * locate open access publications
  * reconcile author profiles
  * reconcile keyword mesh

This library has been guided by collaborative work on community
building and metadata exchange to improve Scholarly Infrastructure,
held at the *2019 Rich Context Workshop*.


## Installation

Prerequisites:

- [Python 3.x](https://www.python.org/downloads/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Dimensions CLI](https://github.com/digital-science/dimcli)
- [Requests](https://2.python-requests.org/en/master/)
- [Selenium](https://github.com/SeleniumHQ/selenium/)

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

NB: be careful not to commit the `rc.cfg` file in Git since it
contains sensitive data such as passwords.

Parameters needed in the configuration file include:

| parameter | value | 
| --- | --- |
| `chrome_exe_path` | path/to/chrome.exe |
| `dimensions_password` | Dimensions API password |
| `email` | personal email address |
| `repec_token` | RePEc API token |

Download the [Chrome webdriver](https://chromedriver.chromium.org/downloads) 
to enable use of Selenium.

For a good (although slightly dated) tutorial for installing and
testing Selenium on Ubuntu Linux, see:
<https://christopher.su/2015/selenium-chromedriver-ubuntu/>


## Usage

```
from richcontext import scholapi as rc_scholapi
import pprint

# initialize the federated API access
schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg", logger=None)

# search parameters for example publications
title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."

# run it...
meta = schol.openaire.title_search(title)

# report results
pprint.pprint(meta)
print("\ntime: {:.3f} ms - {}".format(schol.openaire.elapsed_time, schol.openaire.name))
```


## API Integrations

APIs used to retrieve metadata:

  * [OpenAIRE](https://develop.openaire.eu/)
  * [EuropePMC](https://europepmc.org/RestfulWebService)
  * [Semantic Scholar](http://api.semanticscholar.org/)
  * [Unpaywall](https://unpaywall.org/products/api)
  * [dissemin](https://dissemin.readthedocs.io/en/latest/api.html)
  * [Dimensions](https://docs.dimensions.ai/dsl/api.html)
  * [RePEc](https://ideas.repec.org/api.html)
  * [SSRN](https://www.ssrn.com/)

See `docs/enrich_pubs.ipynb` for example API usage to pull the
federated metadata for a publication.

For more background about *open access publications* see:

> Piwowar H, Priem J, Larivière V, Alperin JP, Matthias L, Norlander B, Farley A, West J, Haustein S. 2017.  
The State of OA: A large-scale analysis of the prevalence and impact of Open Access articles  
*PeerJ Preprints* 5:e3119v1  
<https://doi.org/10.7287/peerj.preprints.3119v1>


## Testing

First, be sure that you're testing the source and not from an
installed library.

Then run unit tests for the APIs which do not require credentials:

```
nose2 -v --pretty-assert
```


## To Do

 * parse HTML-embedded metadata from the web pages for PMC/Pubmed, NIH, etc.
 * [Scholexplorer](http://scholexplorer.openaire.eu/#/)
 * [DataCite and Crossref integrations](https://github.com/NYU-CI/RCApi/issues/8)
 * [PapersWithCode](https://paperswithcode.com/?ref=semscholar)
 * [Springer](https://github.com/srand525/search_springer/blob/master/SpringerFetch.py)

If you'd like to contribute, please see our listings of
[*good first issues*](https://github.com/NYU-CI/RCApi/labels/good%20first%20issue)


## Kudos

Contributors:
[@ceteri](https://github.com/ceteri), 
[@srand525](https://github.com/srand525), 
[@IanMulvany](https://github.com/IanMulvany),
plus many thanks for the inspiring *2019 Rich Context Workshop* notes by 
[@metasj](https://github.com/metasj),
and guidance from
[@claytonrsh](https://github.com/claytonrsh),
[@Juliaingridlane](https://github.com/Juliaingridlane).

