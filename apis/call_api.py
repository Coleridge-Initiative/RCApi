def extract_url(test_case):
    url_list = []
    try:
        native_url = test_case['url']
    except:
        native_url = None
    try:
        dim_url = test_case['dimensions']['linkout']
    except:
        dim_url = None
    if native_url:
        url_list.append(native_url)
    if dim_url:
        url_list.append(dim_url)
    url_list = list(set(url_list))
    return url_list

def extract_doi(test_case):
    doi_list = []
    try:
        native_doi = test_case['doi']
    except:
        native_doi = None
    try:
        dim_doi = test_case['doi']
    except:
        dim_doi = None
    if native_doi:
        doi_list.append(native_doi)
    if dim_doi:
        doi_list.append(dim_doi)
    doi_list = list(set(doi_list))
    return doi_list


def check_ssrn(test_case):
    doi_list = extract_doi(test_case)
    url_list = extract_url(test_case)
    ssrn_doi_list = [d for d in doi_list if 'ssrn' in d]
    ssrn_url_list = [u for u in url_list if 'ssrn' in u]
    if len(ssrn_url_list) > 0:
        ssrn_input = ssrn_url_list[0]
    elif len(ssrn_url_list) == 0 and len(ssrn_doi_list) > 0:
        ssrn_input = ssrn_doi_list[0]
    elif len(ssrn_url_list) == 0 and len(ssrn_doi_list) == 0:
        ssrn_input = None
    return ssrn_input


def assign_apis(test_case):
    ssrn_input = check_ssrn(test_case)
    if ssrn_input != None:
        api_dict = {'available_api':['ssrn']}
    if ssrn_input != None and test_case['title'] != None:
        api_dict['available_api'].append('dimensions')
    if ssrn_input == None and test_case['title'] != None:
        api_dict = {'available_api':['dimensions']}
    test_case.update(api_dict)
    return test_case
