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
    #meta = schol.europepmc.title_search(title)
    meta, message = schol.pubmed.journal_lookup(issn)
    print(meta)

    # report results
    print("\ntime: {:.3f} ms - {}".format(schol.pubmed.elapsed_time, schol.pubmed.name))

    # report profiling
    #schol.stop_profiling(pr)
