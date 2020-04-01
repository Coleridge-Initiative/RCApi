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

    # initialize the API access
    schol = rc_scholapi.ScholInfraAPI(config_file="rc.cfg", logger=None)
    #source = schol.datacite
    source = schol.nsfPar

    # enable this for profiling -- which is quite verbose!
    enable_profiling = False # True

    if enable_profiling:
        pr = schol.start_profiling()

    # search parameters for example use cases
    doi = "10.1016/j.appet.2017.07.006"
    issn = "1932-6203"
    title = "Empirical analysis of potential improvements for high voltage protective algorithms"
    search_term = "NASA NOAA coral"

    # run it...
    if source.has_credentials():
        responses = source.full_text_search(search_term, limit=13, exact_match=True)

        # report results
        if responses[0].message:
            # error case
            print(responses[0].message)
        else:
            for r in responses:
                print(json.dumps(r.meta, indent=4, ensure_ascii=False))

    # report performance
    source.report_perf(responses[0].timing)

    if enable_profiling:
        schol.stop_profiling(pr)
