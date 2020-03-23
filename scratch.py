
from richcontext import scholapi as rc_scholapi
import pprint
import unittest
import warnings


schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")
source = schol.core
doi = "10.1371/journal.pone.0013969"
title = "Caribbean corals in crisis: record thermal stress, bleaching and mortality in 2005".lower()
url = "https://core.ac.uk/download/pdf/143863779.pdf"
author = "Eakin, C. Mark"
journal = "NSUWorks"

if source.has_credentials():
    response = source.title_search(title)
    print(response.title().replace("\n", " ").replace("\t", " "))
    print(response.title().replace("\n", " ").replace("\t", " ").lower() == title)
    print(author in response.authors())
    # print(responses[1].title())
    # print(responses[1].doi())
    # print(responses[1].authors())
    # print(responses[1].url())
    # print(responses[1].journal())
    # print(responses[1].meta)
    