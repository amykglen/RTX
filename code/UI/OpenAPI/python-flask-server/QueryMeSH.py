""" This module defines the class QueryMeSH which connects to APIs at
http://eutils.ncbi.nlm.nih.gov/entrez/eutils for db=mesh, querying information
about a term of unknown origin, primarily to figure out what it is and get a
nice definition for a human.
"""

__author__ = ""
__copyright__ = ""
__credits__ = []
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = "Prototype"

import requests
import requests_cache
import time

def make_throttle_hook(timeout=1.0):
    """
    From: https://requests-cache.readthedocs.io/en/latest/user_guide.html#usage
    Returns a response hook function which sleeps for `timeout` seconds if
    response is not cached
    """
    def hook(response, *args, **kwargs):
        #print("In hook")
        if not getattr(response, 'from_cache', False):
            #print("sleeping "+str(timeout))
            time.sleep(timeout)
        return response
    return hook


class QueryMeSH:

    API_BASE_URL = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils'

    def __init__(self):
        requests_cache.install_cache(cache_name='QueryMeSH.requestCache', backend='sqlite', expire_after=180000)
        self.hooks = make_throttle_hook(0.5)

    def send_query_get(self, entity, url_suffix):
        url_str = self.API_BASE_URL + "/" + entity + url_suffix
        #print(url_str)
        #res = requests.get(url_str, headers={'accept': 'application/json'})
        cache = requests_cache.CachedSession()
        cache.hooks = {'response': self.hooks}
        res = cache.get(url_str, headers={'accept': 'application/json'})
        status_code = res.status_code
        #print("status_code="+str(status_code))
        assert status_code in [200, 404]
        if status_code == 404:
            res = None
        return res


    def findTermAttributesByName(self, term):
        attributes = {}
        attributes["status"] = "UnableToConnect"
        idlist = self.findPotentialTermIds(term)
        if idlist:
            id = self.findTermId(term)
        else:
            attributes["status"] = "TermNotFound"
        return attributes


    def findTermId(self, term):
        id = None
        idlist = self.findPotentialTermIds(term)
        if idlist:
            if len(idlist) == 1:
                id = idlist[0]
            else:
                print("WARNING: multiple returned ids")
                print(idlist)
        return id


    def findTermAttributesAndTypeByName(self, term):
        method = "findTermAttributesAndTypeByName"
        attributes = {}
        attributes["status"] = "UnknownTerm"
        termId = self.findTermId(term)
        if termId:
            attributes = self.findTermAttributesById(termId)
            attributes["type"] = self.findTermTypeById(attributes["parentId"])
            attributes["status"] = "OK"
        return attributes


    def findTermAttributesById(self, termId):
        method = "findPotentialTermIds"
        attributes = {}
        attributes["status"] = "UnableToConnect"

        #### Query MeSH to get information about the specified id
        content = self.send_query_get("esummary.fcgi", "?db=mesh&retmode=json&id=" + termId)
        if content is not None:
            #### Convert text content to JSON
            result = content.json()
            #print(result)
            #### Decode the result
            if type(result) == dict:
                if result["result"]:
                    if result["result"][termId]:
                        attributes["id"] = termId
                        attributes["name"] = result["result"][termId]["ds_meshterms"][0]
                        attributes["description"] = result["result"][termId]["ds_scopenote"]
                        attributes["parentId"] = str(result["result"][termId]["ds_idxlinks"][0]["parent"])
                        attributes["status"] = "OK"
                        return attributes
                    else:
                        print("ERROR: ["+method+"]: result does not have the called termId for termId=" + termId)
                        print(result)
                else:
                    print("ERROR: ["+method+"]: result is not present for term "+term)
                    print(result)
            else:
                print("ERROR: ["+method+"]: result is not a type dict as expected for term "+term)
                print(result)
        return attributes


    def findTermTypeById(self, termId):
        keepGoing = 1
        counter = 0
        while keepGoing:
            attributes = self.findTermAttributesById(termId)
            name = attributes["name"]
            if name:
                #print(attributes)
                if attributes["name"] == "Chemicals and Drugs Category":
                    type = "drug"
                    keepGoing = 0
                elif attributes["name"] == "Diseases Category":
                    type = "disease"
                    keepGoing = 0
                elif attributes["name"] == "Enzymes and Coenzymes":
                    type = "protein"
                    keepGoing = 0
                elif attributes["name"] == "Anatomy Category":
                    type = "anatomical part"
                    keepGoing = 0
                elif attributes["parentId"] == "1000048":
                    type = name
                    keepGoing = 0
                else:
                    type = attributes["name"]
                    termId = attributes["parentId"]
            else:
                print("No name? Time to stop?")
                keepGoing = 0
            counter += 1
            if counter > 7:
                keepGoing = 0
        return type


    def prettyPrintAttributes(self, attributes):
        buffer = ""
        if attributes["status"] == "OK":
            buffer += "<UL>"
            buffer += "<LI> <b>Name:</b> "+attributes["name"]
            buffer += "<LI> <b>Description:</b> "+attributes["description"]
            buffer += "<LI> <b>Type:</b> "+attributes["type"]
            buffer += "<UL>"
        else:
            buffer = "Unable to find that term"
        return buffer


    def findPotentialTermIds(self, term):
        method = "findPotentialTermIds"
        potentialTermIds = None

        #### Query MeSH for the specified term
        content = self.send_query_get("esearch.fcgi", "?db=mesh&retmode=json&term=" + term + '[MeSH Terms]')
        if content is not None:
            #### Convert text content to JSON
            result = content.json()
            #print(result)

            #### Decode the result
            if type(result) == dict:
                if result["esearchresult"]:
                    if result["esearchresult"]["count"] == "0":
                        return potentialTermIds
                    idlist = result["esearchresult"]["idlist"]
                    if type(idlist) == list:
                        potentialTermIds = idlist
                    else:
                        print("ERROR: ["+method+"]: idlist is not of type list for term "+term)
                        print(result)
                else:
                    print("ERROR: ["+method+"]: esearchresult is not present for term "+term)
                    print(result)
            else:
                print("ERROR: ["+method+"]: result is not a type dict as expected for term "+term)
                print(result)
        return potentialTermIds


if __name__ == '__main__':
    q = QueryMeSH()
    if 1 == 1:
        #print(q.findTermAttributesById("68008148"))
        #print(q.findPotentialTermIds("lovastatin"))
        #print(q.findPotentialTermIds("boogerstatin"))
        #termId = q.findTermId("lovastatin")
        #attributes = q.findTermAttributesAndTypeByName("malaria")
        #attributes = q.findTermAttributesAndTypeByName("phenazepam")
        attributes = q.findTermAttributesAndTypeByName("physostigmine")
        print(attributes)
        print(q.prettyPrintAttributes(attributes))

