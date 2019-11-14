# RCApi

APIs for Rich Context Metadata

Use `enrich_pubs.ipynb` to see APIs in action for a publication.


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
  * [Dimensions](https://docs.dimensions.ai/dsl/api.html)
  * SSRN


## Notes about specific APIs

* SSRN tends to not provide journal

### Dimensions
`import RichContextAPI`
`dimensions_title_search(title)`

### EuropePMC
- we can add alt_ids for pmid, pmc. to do

### OpenAire
- we can get a repec id as an alt_id - to do

Lets look to add other metadata fields:
* keywords
* mesh terms
