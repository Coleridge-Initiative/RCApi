#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi
import json
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
    doi = "10.1016/j.appet.2017.07.006"
    issn = "1932-6203"
    title = "Empirical analysis of potential improvements for high voltage protective algorithms"
    source = schol.datacite

    # run it...
    #meta, timing, message = source.journal_lookup(issn)
    meta, timing, message = source.title_search(title)

    if message:
        # error case
        print(message)
    else:
        # report results
        print(json.dumps(meta, indent=4, ensure_ascii=False))
        print("\ntime: {:.3f} ms - {}".format(timing, source.name))

    # report profiling
    #schol.stop_profiling(pr)
