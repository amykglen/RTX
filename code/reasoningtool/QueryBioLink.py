""" This module defines the class QueryBioLink. QueryBioLink class is designed
to communicate with Monarch APIs and their corresponding data sources. The
available methods include:
    * query phenotype for disease
    * query disease for gene
    * query gene for disease
    * query phenotype for gene
    * query gene for pathway
    * query label for disease
    * query label for phenotype
    * query anatomy for gene
    * query gene for anatomy
    * query anatomy for phenotype
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
import CachedMethods
import sys

class QueryBioLink:
    TIMEOUT_SEC = 120
    API_BASE_URL = {
        "get_phenotypes_for_disease": "https://api.monarchinitiative.org/api/bioentity/disease/{disease_id}/phenotypes",
        "get_diseases_for_gene": "https://api.monarchinitiative.org/api/bioentity/gene/{gene_id}/diseases",
        "get_genes_for_disease": "https://api.monarchinitiative.org/api/bioentity/disease/{disease_id}/genes",
        "get_phenotypes_for_gene": "https://api.monarchinitiative.org/api/bioentity/gene/{gene_id}/phenotypes?exclude_automatic_assertions=true&unselect_evidence=true",
        "get_genes_for_pathway": "https://api.monarchinitiative.org/api/bioentity/pathway/{pathway_id}/genes&unselect_evidence=true",
        "get_label_for_disease": "https://api.monarchinitiative.org/api/bioentity/disease/{disease_id}",
        "get_label_for_phenotype": "https://api.monarchinitiative.org/api/bioentity/phenotype/{phenotype_id}",
        "get_anatomies_for_gene": "https://api.monarchinitiative.org/api/bioentity/gene/{gene_id}/expression/anatomy",
        "get_genes_for_anatomy": "https://api.monarchinitiative.org/api/bioentity/anatomy/{anatomy_id}/genes",
        "get_anatomies_for_phenotype": "https://api.monarchinitiative.org/api/bioentity/phenotype/{phenotype_id}/anatomy"
    }

    @staticmethod
    def __access_api(url):
        # print(url)
        try:
            res = requests.get(url,
                               timeout=QueryBioLink.TIMEOUT_SEC)
        except requests.exceptions.Timeout:
            print(url, file=sys.stderr)
            print("Timeout in QueryBioLink for URL: " + url, file=sys.stderr)
            return None
        status_code = res.status_code
        if status_code != 200:
            print(url, file=sys.stderr)
            print("Status code " + str(status_code) + " for url: " + url, file=sys.stderr)
            return None

        return res.json()

    @staticmethod
    def get_label_for_disease(disease_id):
        url = QueryBioLink.API_BASE_URL["get_label_for_disease"].format(disease_id=disease_id)
        results = QueryBioLink.__access_api(url)
        result_str = 'UNKNOWN'
        if results is not None:
            result_str = results['label']
        return result_str

    @staticmethod
    def get_phenotypes_for_disease_desc(disease_id):
        url = QueryBioLink.API_BASE_URL["get_phenotypes_for_disease"].format(disease_id=disease_id)
        results = QueryBioLink.__access_api(url)
        ret_dict = dict()
        if results is None:
            return ret_dict
        res_list = results['objects']
        if len(res_list) > 200:
            print('Number of phenotypes found for disease: ' + disease_id + ' is: ' + str(len(res_list)))
        for phenotype_id_str in res_list:
            phenotype_label_str = QueryBioLink.get_label_for_phenotype(phenotype_id_str)
            ret_dict[phenotype_id_str] = phenotype_label_str

        return ret_dict

    @staticmethod
    def get_diseases_for_gene_desc(gene_id):
        """for a given NCBI Entrez Gene ID, returns a ``set`` of DOI disease identifiers for the gene

        :returns: a ``set`` containing ``str`` disease ontology identifiers
        """
        url = QueryBioLink.API_BASE_URL["get_diseases_for_gene"].format(gene_id=gene_id)
        results = QueryBioLink.__access_api(url)
        ret_data = dict()
        if results is None:
            return ret_data
        
        ret_list = results['objects']
        
        if len(ret_list) > 200:
            print('Number of diseases found for gene ' + gene_id + ' is: ' + str(len(ret_list)))

        for disease_id in ret_list:
            if 'DOID:' in disease_id or 'OMIM:' in disease_id:
                ret_data[disease_id] = QueryBioLink.get_label_for_disease(disease_id)

        return ret_data

    @staticmethod
    def get_genes_for_disease_desc(disease_id):
        url = QueryBioLink.API_BASE_URL["get_genes_for_disease"].format(disease_id=disease_id)

        results = QueryBioLink.__access_api(url)
        ret_list = []
        if results is None:
            return ret_list
        ret_list = results['objects']

        if len(ret_list) > 100:
            print('number of genes found for disease ' + disease_id + ' is: ' + str(len(ret_list)), file=sys.stderr)
        return ret_list

    @staticmethod
    def get_label_for_phenotype(phenotype_id_str):
        url = QueryBioLink.API_BASE_URL["get_label_for_phenotype"].format(phenotype_id=phenotype_id_str)
        results = QueryBioLink.__access_api(url)
        result_str = 'UNKNOWN'
        if results is not None:
            result_str = results['label']
        return result_str

    @staticmethod
    def get_phenotypes_for_gene(gene_id):
        url = QueryBioLink.API_BASE_URL["get_phenotypes_for_gene"].format(gene_id=gene_id)

        results = QueryBioLink.__access_api(url)
        ret_list = []
        if results is None:
            return ret_list
        ret_list = results['objects']

        if len(ret_list) > 200:
            print("Warning, got " + str(len(ret_list)) + " phenotypes for gene " + gene_id, file=sys.stderr)

        return ret_list

    @staticmethod
    def get_phenotypes_for_gene_desc(ncbi_entrez_gene_id):
        phenotype_id_set = QueryBioLink.get_phenotypes_for_gene(ncbi_entrez_gene_id)
        ret_dict = dict()
        for phenotype_id_str in phenotype_id_set:
            phenotype_label_str = QueryBioLink.get_label_for_phenotype(phenotype_id_str)
            if 'HP:' in phenotype_id_str:
                ret_dict[phenotype_id_str] = phenotype_label_str
        return ret_dict

    @staticmethod
    def get_anatomies_for_gene(gene_id):
        """for a given NCBI Entrez Gene ID, returns a ``dict`` of Anatomy IDs and labels for the gene

        :returns: a ``dict`` of <anatomy_ID, label>
        """
        url = QueryBioLink.API_BASE_URL["get_anatomies_for_gene"].format(gene_id=gene_id)

        results = QueryBioLink.__access_api(url)
        ret_dict = dict()
        if results is None:
            return ret_dict
        res_dict = results['associations']
        ret_dict = dict(map(lambda r: (r["object"]["id"], r["object"]["label"]), res_dict))

        if len(ret_dict) > 200:
            print("Warning, got {} anatomies for gene {}".format(len(ret_dict), gene_id))

        return ret_dict

    @staticmethod
    def get_genes_for_anatomy(anatomy_id):
        """for a given Anatomy ID, returns a ``list`` of Gene ID for the anatomy

        :returns: a ``list`` of gene ID
        """
        url = QueryBioLink.API_BASE_URL["get_genes_for_anatomy"].format(anatomy_id=anatomy_id)

        results = QueryBioLink.__access_api(url)
        ret_list = []
        if results is None:
            return ret_list
        res_dict = results['associations']
        ret_list = list(map(lambda r: r["subject"]["id"], res_dict))

        if len(ret_list) > 200:
            print("Warning, got {} genes for anatomy {}".format(len(ret_list), anatomy_id))

        return ret_list

    @staticmethod
    def get_anatomies_for_phenotype(phenotype_id):
        """for a given phenotype ID, returns a ``dict`` of Anatomy IDs and labels for the phenotype

        :returns: a ``dict`` of <anatomy_ID, label>
        """
        url = QueryBioLink.API_BASE_URL["get_anatomies_for_phenotype"].format(phenotype_id=phenotype_id)

        results = QueryBioLink.__access_api(url)
        ret_dict = ()
        if results is None:
            return ret_dict
        
        ret_dict = dict(map(lambda r: (r["id"], r["label"]), results))

        if len(ret_dict) > 200:
            print("Warning, got {} anatomies for phenotype {}".format(len(ret_dict), phenotype_id))

        return ret_dict

if __name__ == '__main__':
    print(QueryBioLink.get_phenotypes_for_disease_desc("OMIM:605543"))
    print(QueryBioLink.get_genes_for_disease_desc("OMIM:XXXXXX"))
    print(QueryBioLink.get_genes_for_disease_desc("OMIM:605543"))
    print(QueryBioLink.get_phenotypes_for_gene_desc("NCBIGene:1080"))  # test for issue #22
    print(QueryBioLink.get_diseases_for_gene_desc("NCBIGene:407053"))
    print(QueryBioLink.get_diseases_for_gene_desc("NCBIGene:100048912"))
    print(QueryBioLink.get_phenotypes_for_gene_desc("NCBIGene:4750"))
    print(QueryBioLink.get_phenotypes_for_gene("NCBIGene:4750"))
    print(QueryBioLink.get_diseases_for_gene_desc("NCBIGene:4750"))
    print(QueryBioLink.get_diseases_for_gene_desc("NCBIGene:1111111"))
    print(QueryBioLink.get_label_for_disease("DOID:1498"))
    print(QueryBioLink.get_label_for_disease("OMIM:605543"))
    print(QueryBioLink.get_label_for_phenotype("HP:0000003"))
    print(QueryBioLink.get_anatomies_for_gene("NCBIGene:407053"))
    print(QueryBioLink.get_genes_for_anatomy("UBERON:0000006"))
    print(QueryBioLink.get_anatomies_for_phenotype("HP:0000003"))
