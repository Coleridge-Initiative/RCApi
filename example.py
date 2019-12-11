#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import logging
import pprint
import requests
import sys


######################################################################
## main entry point

if __name__ == "__main__":
    # logging is optional: to debug, set the `logger` parameter
    # when initializing the `ScholInfraAPI` object
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger("RichContext")

    # initialize the federated API access
    schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg", logger=None)

    # search parameters for example publications
    title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
    doi = "10.1016/j.appet.2017.07.006"

    # run it...
    meta = schol.europepmc.title_search(title)

    # report results
    print(meta)
    print("\ntime: {:.3f} ms - {}".format(schol.openaire.elapsed_time, schol.openaire.name))
