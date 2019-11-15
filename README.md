# RCApi

APIs for Rich Context Metadata


## Instructions

1. Download the [Chrome webdriver](https://chromedriver.chromium.org/downloads) to enable Selenium to run, which is needed for SSRN.
2. Create the config file template `rc_template.cfg` to `rc.cfg` which you populate with your own credentials. Don't commit the `rc.cfg` file in Git.


### Config File

| parameter | value | 
| --- | --- |
| `chrome_exe_path` | path/to/chrome.exe |
| `dimensions_username` | Dimensions API username |
| `dimensions_password` | Dimensions API password |
| `repec_token` | RePEc API token |


## API integrations to retrieve metadata for Rich Context

APIs used:

  * [RePEc](https://ideas.repec.org/api.html)
  * [OpenAIRE](https://develop.openaire.eu/)
  * [EuropePMC](https://europepmc.org/RestfulWebService)
  * [Semantic Scholar](http://api.semanticscholar.org/)
  * [Dimensions](https://docs.dimensions.ai/dsl/api.html)
  * SSRN


Use `enrich_pubs.ipynb` to see APIs in action for a publication.
