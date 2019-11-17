# RCApi

API integrations for federating metadata lookup across multiple
scholarly infrastructure providers.

For the development of the Rich Context knowledge graph this library
is used to identify:

  * datasets used for research projects
  * locating open access publications
  * reconciling author profiles
  * reconciling keyword mesh


## Installation

Copy the configuration file template `rc_template.cfg` to `rc.cfg`
then populate it with your credentials.

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


## API Integrations

APIs used to retrieve metadata:

  * [RePEc](https://ideas.repec.org/api.html)
  * [OpenAIRE](https://develop.openaire.eu/)
  * [EuropePMC](https://europepmc.org/RestfulWebService)
  * [Semantic Scholar](http://api.semanticscholar.org/)
  * [Unpaywall](https://unpaywall.org/products/api)
  * [Dimensions](https://docs.dimensions.ai/dsl/api.html)
  * SSRN


See `enrich_pubs.ipynb` for example API usage to pull federated
metadata for a publication.

For more background about *open access publications* see:

> Piwowar H, et al., 2017.  
The State of OA: A large-scale analysis of the prevalence and impact of Open Access articles  
*PeerJ Preprints* 5:e3119v1  
<https://doi.org/10.7287/peerj.preprints.3119v1>
