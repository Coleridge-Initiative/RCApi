#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import pprint
import requests


######################################################################
## main entry point

if __name__ == "__main__":
    title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
    doi = "10.1016/j.appet.2017.07.006"

    schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg")

    meta = schol.dissemin_publication_lookup(doi)
    pprint.pprint(meta)

