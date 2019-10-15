import requests
import time
import pandas as pd
import math
import numpy as np
from json import JSONDecodeError

class DimensionsSearchAPIClient( object ):
    
    
    #==========================================================================#
    # ! CONSTANTS-ish
    #==========================================================================#

    
    # capture all parts of 'https://app.dimensions.ai/api'
    DIMENSIONS_SEARCH_API_BASE_DOMAIN = ".dimensions.ai"
    DIMENSIONS_SEARCH_API_DEFAULT_DOMAIN = "app{}".format( DIMENSIONS_SEARCH_API_BASE_DOMAIN )
    DIMENSIONS_SEARCH_API_PROTOCOL = "https"
    DIMENSIONS_SEARCH_API_DEFAULT_URL = "{}://{}/api".format( DIMENSIONS_SEARCH_API_PROTOCOL, DIMENSIONS_SEARCH_API_DEFAULT_DOMAIN )
    
    # API Pages
    DIMENSIONS_SEARCH_API_AUTH_PAGE = "auth.json"
    DIMENSIONS_SEARCH_API_SEARCH_PAGE = "dsl.json"
    
    # Dimensions Search API (DSA) traits
    DSA_MAX_IN_ITEMS_MIN = 0
    DSA_MAX_IN_ITEMS_MAX = 512
    DSA_MAX_RETURN_MAX = 1000
    DSA_MAX_OVERALL_RETURNS_MAX = 50000
    
    # DSA Entity Types
    DSA_ENTITY_TYPE_PUBLICATIONS = "publications"
    
    # DSA Entity Type "publications" Fields
    # - full list is here: https://docs.dimensions.ai/dsl/data-sources.html#publications
    DSA_PUBLICATIONS_FIELD_ALTMETRIC = "altmetric"
    DSA_PUBLICATIONS_FIELD_AUTHOR_AFFILIATIONS = "author_affiliations"
    DSA_PUBLICATIONS_FIELD_DATE = "date"
    DSA_PUBLICATIONS_FIELD_DOI = "doi"
    DSA_PUBLICATIONS_FIELD_FIELD_CITATION_RATIO = "field_citation_ratio"
    DSA_PUBLICATIONS_FIELD_FOR = "FOR"
    DSA_PUBLICATIONS_FIELD_FUNDER_COUNTRIES = "funder_countries"
    DSA_PUBLICATIONS_FIELD_FUNDERS = "funders"
    DSA_PUBLICATIONS_FIELD_HRCS_HC = "HRCS_HC"
    DSA_PUBLICATIONS_FIELD_HRCS_RAC = "HRCS_RAC"
    DSA_PUBLICATIONS_FIELD_ID = "id"
    DSA_PUBLICATIONS_FIELD_ISSUE = "issue"
    DSA_PUBLICATIONS_FIELD_JOURNAL = "journal"
    DSA_PUBLICATIONS_FIELD_LINKOUT = "linkout"
    DSA_PUBLICATIONS_FIELD_MESH_TERMS = "mesh_terms"
    DSA_PUBLICATIONS_FIELD_OPEN_ACCESS_CATEGORIES = "open_access_categories"
    DSA_PUBLICATIONS_FIELD_PMCID = "pmcid"
    DSA_PUBLICATIONS_FIELD_PMID = "pmid"
    DSA_PUBLICATIONS_FIELD_PAGES = "pages"
    DSA_PUBLICATIONS_FIELD_PUBLISHER = "publisher"   
    DSA_PUBLICATIONS_FIELD_RCDC = "RCDC"
    DSA_PUBLICATIONS_FIELD_RECENT_CITATIONS = "recent_citations"
    DSA_PUBLICATIONS_FIELD_RELATIVE_CITATION_RATIO = "relative_citation_ratio"
    DSA_PUBLICATIONS_FIELD_RESEARCH_ORGS = "research_orgs"
    DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_CITIES = "research_org_cities"
    DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_STATE_CODES = "research_org_state_codes"
    DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_STATE_NAMES = "research_org_state_names"
    DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_COUNTRIES = "research_org_countries"
    DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_COUNTRY_NAMES = "research_org_country_names"
    DSA_PUBLICATIONS_FIELD_SUPPORTING_GRANT_IDS = "supporting_grant_ids"
    DSA_PUBLICATIONS_FIELD_TIMES_CITED = "times_cited"
    DSA_PUBLICATIONS_FIELD_TITLE = "title"
    DSA_PUBLICATIONS_FIELD_TYPE = "type"
    DSA_PUBLICATIONS_FIELD_VOLUME = "volume"
    DSA_PUBLICATIONS_FIELD_YEAR = "year"

    # default field return list for publications.
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST = []
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_ID )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_DOI )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_PMID )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_PMCID )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_TITLE )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_JOURNAL )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_YEAR )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_OPEN_ACCESS_CATEGORIES )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_AUTHOR_AFFILIATIONS )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RESEARCH_ORGS )
    DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_FOR )
    
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST = []
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_PUBLISHER )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_MESH_TERMS )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_VOLUME )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_ISSUE )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_PAGES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_TYPE )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_CITIES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_STATE_CODES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_STATE_NAMES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_COUNTRIES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RESEARCH_ORG_COUNTRY_NAMES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_FUNDERS )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_FUNDER_COUNTRIES )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_SUPPORTING_GRANT_IDS )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_TIMES_CITED )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RECENT_CITATIONS )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_RELATIVE_CITATION_RATIO )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_FIELD_CITATION_RATIO )
    DSA_PUBLICATIONS_EXTRA_FIELD_LIST.append( DSA_PUBLICATIONS_FIELD_LINKOUT )
    

    #==========================================================================#
    # ! class methods
    #==========================================================================#


    @classmethod
    def create_default_return_fields_for_publications( cls,
                                                       include_extras_IN = False,
                                                       include_square_brackets_IN = False,
                                                       return_list_IN = False ):
        
        # return reference
        value_OUT = ""
        
        # declare variables
        debug_flag = False
        field_list = None
        
        field_list = cls.DSA_PUBLICATIONS_DEFAULT_FIELD_LIST.copy()
        
        if ( include_extras_IN == True ):
        
            # append the extras to the list.
            if ( debug_flag ):
                print( "Include extras!" )
            #-- END DEBUG --#
            field_list.extend( cls.DSA_PUBLICATIONS_EXTRA_FIELD_LIST )
            
        else:
        
            if ( debug_flag ):
                print( "Don't include extras!" )
            #-- END DEBUG --#
        
        #-- END check to see if we want extras --#
        
        if ( debug_flag ):
            print( "Field list: {}".format( field_list ) )
        #-- END DEBUG --#
        
        # return list?
        if ( return_list_IN == False ):

            # convert to string
            value_OUT = "+".join( field_list )
            
            if ( include_square_brackets_IN == True ):
            
                value_OUT = "[{}]".format( value_OUT )
                
            #-- END check to see if square brackets. --#
            
        else:
        
            value_OUT = field_list
        
        #-- END check to see if we convert to list. --#
        
        return value_OUT
    
    #-- END class method create_default_field_list_for_publications() --#


    #==========================================================================#
    # ! __init__() method
    #==========================================================================#


    # __init__ and instance variables
    def __init__( self ):

        # user information
        self.username = None
        self.password = None
        
        # auth token.
        self.auth_token = None
        
        # settings for API interaction
        self.search_api_url = self.DIMENSIONS_SEARCH_API_DEFAULT_URL
        self.max_in_items = 100           # Filter operator 'in' requires 0 < items < 512
        self.max_returns = 1000           # Limit exceeds maximum allowed limit 1000
        self.max_overall_returns = 50000  # Offset - cannot exceed 50,000.
        
        # debug
        self.debug_flag = False
        
    #-- END init method. --#
    
    
    #==========================================================================#
    # ! instance methods
    #==========================================================================#

    
    def create_login_json( self ):
    
        # return reference
        value_OUT = None
        
        # declare variables
        username = None
        password = None
        
        # get username and password
        username = self.get_username()
        password = self.get_password()
        
        # render JSON dictionary.        
        value_OUT = {}
        value_OUT[ 'username' ] = username
        value_OUT[ 'password' ] = password
       
        return value_OUT
    
    #-- END method create_login_json() --#


    def execute_query( self, query_string_IN, api_url_IN = None ):
        
        # return reference
        results_OUT = None
        
        # declare variables
        auth_token = None
        headers = None
        api_url = None
        search_url = None
        search_response = None
        response_text = None
        
        # get auth token
        auth_token = self.get_auth_token()        
    
        # Create http header using the generated token.
        headers = { 'Authorization': "JWT " + auth_token }
    
        if ( self.debug_flag == True ):
            print( "search: {}".format( query_string_IN ) )
        #-- END check to see if debugging --#
        
        # base URL passed in?
        api_url = self.get_search_api_url()
        if ( ( api_url_IN is not None ) and ( api_url_IN != "" ) ):
        
            # URL passed in.  Use it.
            api_url = api_url_IN
        
        #-- END check to see if API URL passed in. --#
        
        # build URL
        search_url = "{}/{}".format( api_url, self.DIMENSIONS_SEARCH_API_SEARCH_PAGE )
        
        # Execute DSL query.
        search_response = requests.post( search_url, data = query_string_IN, headers = headers )
    
        # does it contain JSON?
        response_text = search_response.text
        if ( ( response_text is not None ) and ( response_text != "" ) and ( response_text.find( "<html>" ) == -1 ) ):
            
            # try to convert to JSON for return
            try:
                results_OUT = search_response.json()
            except JSONDecodeError:
                print( "Non-JSON response:" )
                print( response_text )
                results_OUT = "ERROR - JSON parse failed: \n{}".format( response_text )
            #-- END try to parse JSON --#
    
        else:
            
            print( "Non-JSON response:" )
            print( response_text )
            results_OUT = "ERROR - Non-JSON response: \n{}".format( response_text )
            
        #-- END check to see if empty response. --#
            
        return results_OUT
        
    #-- END method execute_query() --#
    

    def get_auth_token( self, api_url_IN = None ):
    
        # return reference
        value_OUT = None
        
        # declare variables
        api_url = None
        login_url = None
        login_json = None
        login_response = None
        login_response_json = None
        auth_token = None
        
        # retrieve existing token.
        value_OUT = self.auth_token
        
        # set?
        if ( ( value_OUT is None ) or ( value_OUT == "" ) ):

            # no.  Need to authenticate.        

            # base URL passed in?
            api_url = self.get_search_api_url()
            if ( ( api_url_IN is not None ) and ( api_url_IN != "" ) ):
            
                # URL passed in.  Use it.
                api_url = api_url_IN
            
            #-- END check to see if API URL passed in. --#
        
            # get login JSON
            login_url = "{}/{}".format( api_url, self.DIMENSIONS_SEARCH_API_AUTH_PAGE )
            login_json = self.create_login_json()
            
            # Send credentials to login url to retrieve token.
            login_response = requests.post( login_url, json = login_json )
            login_response.raise_for_status()
            
            # retrieve auth token.
            login_response_json = login_response.json()
            auth_token = login_response_json.get( "token", None )
            
            # store it
            self.set_auth_token( auth_token )
            
            # sanity check - return results of another call to get.
            value_OUT = self.get_auth_token()
            
        #-- END check to see if token is not already set. --#
       
        return value_OUT
    
    #-- END method get_auth_token() --#


    def get_max_in_items( self ):
    
        # return reference
        value_OUT = None
        
        value_OUT = self.max_in_items
       
        return value_OUT
    
    #-- END method get_max_in_items() --#


    def get_max_overall_returns( self ):
    
        # return reference
        value_OUT = None
        
        value_OUT = self.max_overall_returns
       
        return value_OUT
    
    #-- END method get_max_overall_returns() --#


    def get_max_return( self ):
    
        # return reference
        value_OUT = None
        
        value_OUT = self.max_return
       
        return value_OUT
    
    #-- END method get_max_return() --#


    def get_password( self ):
    
        # return reference
        value_OUT = None
        
        value_OUT = self.password
       
        return value_OUT
    
    #-- END method get_password() --#


    def get_search_api_url( self ):
    
        # return reference
        value_OUT = None
        
        value_OUT = self.search_api_url
       
        return value_OUT
    
    #-- END method get_search_api_url() --#


    def get_username( self ):
    
        # return reference
        value_OUT = None
        
        value_OUT = self.username
       
        return value_OUT
    
    #-- END method get_username() --#


    def load_password_from_file( self, path_IN = "./dimensions_password" ):
    
        # return reference
        value_OUT = None

        # declare variables
        password_file_path = None
        password_file = None
        
        # read file
        password_file_path = path_IN
        with open( password_file_path, 'r' ) as password_file:
            
            password = myfile.read().strip()

            # set value
            self.set_password( password )

        #-- END with --#
        
        # return it
        value_OUT = self.get_password()
       
        return value_OUT
    
    #-- END method set_password() --#


    def pull_data_for_in_list( self,
                               search_string_IN,
                               in_list_IN,
                               in_type_IN,
                               return_type_IN,
                               max_in_items_IN = None,
                               max_return_IN = None,
                               max_overall_returns_IN = None ):
    
        # return reference
        results_OUT = None
        
        # declare variables
        full_resp = None
        max_in_items = None
        max_return = None
        max_overall_returns = None
        temp_value = None
        i = None
        min_i = None
        max_i = None
        in_list_length = None
        break_list_into = None
        in_request_count = None
        in_subset_list = None
        in_subset_list_string = None
        query = None
        j = None
        loop = None
        query_subset = None
        resp = None
        
        # initialize API traits
        
        # --> max_in_items
        max_in_items = self.get_max_in_items()
        if ( max_in_items_IN is not None ):
            max_in_items = max_in_items_IN
        #-- END check to see if anything passed in. --#
        
        # --> max_return
        max_return = self.get_max_return()
        if ( max_return_IN is not None ):
            max_return = max_return_IN
        #-- END check to see if anything passed in. --#

        # --> max_overall_returns
        max_overall_returns = self.get_max_overall_returns()
        if ( max_overall_returns_IN is not None ):
            max_overall_returns = max_overall_returns_IN
        #-- END check to see if anything passed in. --#
        
        # create list to hold results
        full_resp = []
        
        # figure out how many requests we need to make
        in_list_length = len( in_list_IN )
        break_list_into = len( in_list_IN ) / max_in_items
        in_request_count = math.ceil( break_list_into )
        
        # loop the number of times we will need to process all IN list items.
        for i in range( in_request_count ):

            # figure out min and max for this iteration through the loop.
            min_i = i * max_in_items
            max_i = min( ( i + 1 ) * max_in_items, len( in_list_IN ) )
            print('Querying: {}-{}/{} {}...'.format( min_i, max_i, len( in_list_IN ), in_type_IN ), end = '\r' )
    
            # create IN list for the current IN range.
            in_subset_list = in_list_IN[ min_i : max_i ]
            in_subset_list_string = "\"" + "\", \"".join( in_subset_list ) + "\""
            query = search_string_IN.format( in_subset_list_string )
            
            if ( self.debug_flag == True ):
                print( "DEBUG: query = {}".format( query ) )
            #-- END check to see if debug --#
    
            j = 0
            loop = True
            while loop == True:
                
                # add limit and skip to query.
                query_subset = query + " limit {} skip {}".format( max_return, max_return * j )
                resp = self.execute_query( query_subset )

                # check response.
                if resp == "RESPONSE ERROR":
                    print( "\nRESPONSE ERROR on i={} and j={}.\n".format( i, j ) )
                else:
                    # add respnse items to full response.
                    full_resp.extend( resp[ return_type_IN ] )
    
                    # was this response less than the max (so we are out of results)?
                    if ( len( resp[ return_type_IN ] ) < max_return ):

                        # yes - fewer than max - end loop
                        loop = False

                    #-- END check to see if we have exceeded max return. --#

                #-- END check response --#
                    
                # increment loop counter.
                j += 1
    
                # have we exceeded the number of overall requested returns?
                if max_return * ( j + 1 ) > max_overall_returns:

                    # yes - end loop.
                    loop = False
                    
                #-- END check to see if we've exceeded requested overall return count --#
    
                # sleep for a bit to not spam API.
                time.sleep(3)
    
            #-- END loop over chunked subset list --#
            
            # get total count.
            count = resp['_stats']['total_count']
            if resp['_stats']['total_count']>=max_overall_returns:
                print("\nATTENTION! {} {} overall, pulled only {}.\n".format(count, return_type_IN, max_return*j-1))
            #-- END check to see if we are over the total count.
    
        #-- END loop over IN list. --#

        print("\nDone !")

        results_OUT = full_resp
    
        return results_OUT
        
    #-- END method pull_data() --#
    

    def request_pubs_metadata( self, doi_list_IN = None, fields_to_return_list_IN = None, api_url_IN = None ):
        
        # return reference
        results_OUT = None
        
        # declare variables
        search_string = None
        fields_to_return_string = None

        # got a list?
        if ( doi_list_IN is not None ):

            # got a list - build search string for pull_data_for_in_list()
            search_string = "search " + self.DSA_ENTITY_TYPE_PUBLICATIONS
            search_string += " where doi in [{}]"
            search_string += " return publications"
            
            # got a list of fields to return?
            if ( ( fields_to_return_list_IN is not None ) and ( len( fields_to_return_list_IN ) > 0 ) ):
            
                # we do have a list - convert to "+"-separated string list...
                fields_to_return_string = "+".join( fields_to_return_list_IN )
                
                # ...and append it.
                search_string += " [{}]".format( fields_to_return_string )
                
            #-- END check to see if fields to return are specified. --#
            
            # call pulldata_for_in_list()
            results_OUT = self.pull_data_for_in_list( search_string_IN = search_string,
                                                      in_list_IN = doi_list_IN,
                                                      in_type_IN = 'doi',
                                                      return_type_IN = self.DSA_ENTITY_TYPE_PUBLICATIONS )
            
        else:
            
            print( "ERROR: no doi list passed in ( {} ), nothing to do.".format( doi_list_IN ) )
            results_OUT = None
            
        #-- END check to see if empty response. --#
            
        return results_OUT
        
    #-- END method request_pubs_metadata() --#
    

    def request_pubs_metadata_for_doi( self, doi_IN = None, fields_to_return_list_IN = None, api_url_IN = None ):
        
        # return reference
        results_OUT = None
        
        # declare variables
        doi_list = None

        # got a list?
        if ( ( doi_IN is not None ) and ( doi_IN != "" ) ):

            # put doi in list, then call request_pubs_metadata.
            doi_list = []
            doi_list.append( doi_IN )
            results_OUT = self.request_pubs_metadata( doi_list, fields_to_return_list_IN, api_url_IN )
            
        else:
            
            print( "ERROR: no doi passed in ( {} ), nothing to do.".format( doi_IN ) )
            results_OUT = None
            
        #-- END check to see if empty response. --#
            
        return results_OUT
        
    #-- END method request_pubs_metadata_for_doi() --#
    

    def set_auth_token( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # set value
        self.auth_token = value_IN
        
        # return it
        value_OUT = self.get_auth_token()
       
        return value_OUT
    
    #-- END method set_auth_token() --#


    def set_max_in_items( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # make sure value is within allowed limits.
        if ( ( value_IN > self.DSA_MAX_IN_ITEMS_MIN ) and ( value_IN <= self.DSA_MAX_IN_ITEMS_MAX ) ):
        
            # set value
            self.max_in_items = value_IN
            
            # retrieve value
            value_OUT = self.get_max_in_items()
            
        else:
        
            print( "ERROR: max_in_items value {} is outside of allowed range {} < value < {}".format( value_IN, self.DSA_MAX_IN_ITEMS_MIN, self.DSA_MAX_IN_ITEMS_MAX ) )
            value_OUT = None
            
        #-- END check to see if value is in range.
        
        return value_OUT
    
    #-- END method set_max_in_items() --#


    def set_max_overall_returns( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # make sure value is within allowed limits.
        if ( value_IN <= self.DSA_MAX_OVERALL_RETURNS_MAX ):
        
            # set value
            self.max_overall_returns = value_IN
            
            # retrieve value
            value_OUT = self.get_max_overall_returns()
            
        else:
        
            print( "ERROR: max_overall_returns value {} is greater than maximum allowed value {}".format( value_IN, self.DSA_MAX_OVERALL_RETURNS_MAX ) )
            value_OUT = None
            
        #-- END check to see if value is in range.
        
        return value_OUT
    
    #-- END method set_max_overall_returns() --#


    def set_max_return( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # make sure value is within allowed limits.
        if ( value_IN <= self.DSA_MAX_RETURN_MAX ):
        
            # set value
            self.max_return = value_IN
            
            # retrieve value
            value_OUT = self.get_max_return()
            
        else:
        
            print( "ERROR: max_return value {} is greater than maximum allowed value {}".format( value_IN, self.DSA_MAX_RETURN_MAX ) )
            value_OUT = None
            
        #-- END check to see if value is in range.
        
        return value_OUT
    
    #-- END method set_max_return() --#


    def set_password( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # set value
        self.password = value_IN
        
        # return it
        value_OUT = self.get_password()
       
        #return value_OUT sbr commented this out - don't want pw being printed out
#         print('API credentials have been set')
        
    
    #-- END method set_password() --#


    def set_search_api_url( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # set value
        self.search_api_url = value_IN
        
        # return it
        value_OUT = self.get_search_api_url()
       
        return value_OUT
    
    #-- END method set_search_api_url() --#


    def set_username( self, value_IN ):
    
        # return reference
        value_OUT = None
        
        # set value
        self.username = value_IN
        
        # return it
        value_OUT = self.get_username()
       
        return value_OUT
    
    
    #-- END method set_username() --#


#-- END class DimensionsSearchAPIClient --#

