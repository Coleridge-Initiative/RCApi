# RCApi

APIs for Rich Context Metadata

Use `enrich_pubs.ipynb` to see APIs in action for a publication.


## Instructions

1. Download the [Chrome webdriver](https://chromedriver.chromium.org/downloads) to enable Selenium to run, which is needed for SSRN.
2. Create the config file template `rc_template.cfg` to `rc.cfg` which you populate with your own credentials. Don't commit the `rc.cfg` file in Git.


### Config File

| parameter | value | 
| --- | --- |
| `username` | Dimensions API username |
| `password` | Dimensions API password |
| `chrome_exe_path` | path/to/chrome.exe |


## API integrations to retrieve metadata for Rich Context

APIs used:

  * [Dimensions](https://docs.dimensions.ai/dsl/api.html)
  * OpenAIRE
  * SSRN
  * EuropePMC


## Notes on APIs
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


#### To Do
##### Add Apis:
* PMC/Pubmed
* RePEc
