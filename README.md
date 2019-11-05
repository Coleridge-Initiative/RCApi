# RCApi
APIs for Rich Context Metadata

use `enrich_pubs.ipynb` to see apis in action on a publication.

### Instructions:
1. Download Chrome webdriver [here](https://chromedriver.chromium.org/downloads) to enable Selenium to run, which is needed to grab metadata from SSRN.
2. Create a config file and name it `api_config.cfg`. 
The file should include: <br /> 
`username = <your dimensions api access username>` <br /> 
`password = <your dimensions api access password>`<br /> 
`chrome_exe_path = <path/to/chrome.exe>`<br /> 

### Library of API calls to retrieve Rich Context Metadata

APIs used:
* [Dimensions](https://docs.dimensions.ai/dsl/api.html)
* OpenAIRE
* SSRN
* EuropePMC



### Notes on APIs
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