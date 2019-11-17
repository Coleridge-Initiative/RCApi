#!/usr/bin/env python
# encoding: utf-8

from richcontext import scholapi as rc_scholapi


######################################################################
## main entry point

if __name__ == "__main__":

    doi = "10.1016/j.appet.2017.07.006"
    email = "info@derwen.ai"

    results = rc_scholapi.unpaywall_publication_lookup(doi, email)
    print(results)
