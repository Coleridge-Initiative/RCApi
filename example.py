#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import logging
import pprint
import sys


######################################################################
## main entry point

if __name__ == "__main__":
    # logging is optional: to debug, set the `logger` parameter
    # when initializing the `ScholInfraAPI` object
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
    logger = logging.getLogger("RichContext")

    # initialize the federated API access
    schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg", logger=None)

    # enable this for profiling -- which is quite verbose!
    #pr = schol.start_profiling()

    # search parameters for example use cases
    title = "Deal or no deal? The prevalence and nutritional quality of price promotions among U.S. food and beverage purchases."
    doi = "10.1016/j.appet.2017.07.006"
    issn = "1932-6203"

    # run it...
    #meta, timing, message = schol.europepmc.title_search(title)
    meta, timing, message = schol.pubmed.journal_lookup(issn)

    if message:
        # error case
        print(message)
    else:
        # report results
        print(meta)
        print("\ntime: {:.3f} ms - {}".format(timing, schol.pubmed.name))

    # report profiling
    #schol.stop_profiling(pr)
