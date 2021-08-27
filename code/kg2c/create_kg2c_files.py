#!/bin/env python3
"""
This script creates a canonicalized version of KG2 stored in various formats, including TSV files ready for import
into neo4j. The files are created in the directory this script is in.
Usage: python3 create_kg2c_files.py [--test]
"""
import argparse
import ast
import csv
import gc
import json
import logging
import os
import pathlib
import pickle
import re
import sqlite3
import subprocess
import sys
import time

from datetime import datetime
from multiprocessing import Pool
from typing import List, Dict, Tuple, Union, Optional, Set

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import select_best_description
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../ARAX/NodeSynonymizer/")
from node_synonymizer import NodeSynonymizer
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../ARAX/BiolinkHelper/")
from biolink_helper import BiolinkHelper

KG2C_ARRAY_DELIMITER = "ǂ"  # Need to use a delimiter that does not appear in any list items (strings)
KG2PRE_ARRAY_DELIMITER = ";"
KG2C_DIR = f"{os.path.dirname(os.path.abspath(__file__))}"


PROPERTIES_LOOKUP = {
    "nodes": {
        "id": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "name": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "category": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "iri": {"type": str, "in_kg2pre": True, "in_kg2c_lite": False},
        "description": {"type": str, "in_kg2pre": True, "in_kg2c_lite": False},
        "all_categories": {"type": list, "in_kg2pre": False, "in_kg2c_lite": True, "use_as_labels": True},
        "publications": {"type": list, "in_kg2pre": True, "in_kg2c_lite": False},
        "equivalent_curies": {"type": list, "in_kg2pre": False, "in_kg2c_lite": False},
        "all_names": {"type": list, "in_kg2pre": False, "in_kg2c_lite": False},
        "expanded_categories": {"type": list, "in_kg2pre": False, "in_kg2c_lite": False}
    },
    "edges": {
        "id": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "subject": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "object": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "predicate": {"type": str, "in_kg2pre": True, "in_kg2c_lite": True},
        "provided_by": {"type": list, "in_kg2pre": True, "in_kg2c_lite": False},
        "publications": {"type": list, "in_kg2pre": True, "in_kg2c_lite": False},
        "kg2_ids": {"type": list, "in_kg2pre": False, "in_kg2c_lite": False},
        "publications_info": {"type": dict, "in_kg2pre": True, "in_kg2c_lite": False}
    }
}


def _convert_list_to_string_encoded_format(input_list_or_str: Union[List[str], str]) -> Union[str, List[str]]:
    if isinstance(input_list_or_str, list):
        filtered_list = [item for item in input_list_or_str if item]  # Get rid of any None items
        str_items = [item for item in filtered_list if isinstance(item, str)]
        if len(str_items) < len(filtered_list):
            logging.warning(f"  List contains non-str items (this is unexpected; I'll exclude them)")
        return KG2C_ARRAY_DELIMITER.join(str_items)
    else:
        return input_list_or_str


def _merge_two_lists(list_a: List[any], list_b: List[any]) -> List[any]:
    unique_items = list(set(list_a + list_b))
    return [item for item in unique_items if item]


def _get_edge_key(subject: str, object: str, predicate: str) -> str:
    return f"{subject}--{predicate}--{object}"


def _get_headers(header_file_path: str) -> List[str]:
    with open(header_file_path) as header_file:
        reader = csv.reader(header_file, delimiter="\t")
        headers = [row for row in reader][0]
    processed_headers = [header.split(":")[0] for header in headers]
    return processed_headers


def _clean_up_description(description: str) -> str:
    # Removes all of the "UMLS Semantic Type: UMLS_STY:XXXX;" bits from descriptions
    return re.sub("UMLS Semantic Type: UMLS_STY:[a-zA-Z][0-9]{3}[;]?", "", description).strip().strip(";")


def _load_property(raw_property_value_from_tsv: str, property_type: any) -> Union[list, str, dict]:
    if property_type is str:
        return raw_property_value_from_tsv
    elif property_type is list:
        split_string = raw_property_value_from_tsv.split(KG2PRE_ARRAY_DELIMITER)
        processed_list = [item.strip() for item in split_string if item]
        return processed_list
    elif property_type is dict:
        # For now, publications_info is the only dict property
        return _load_publications_info(raw_property_value_from_tsv, "none")
    else:
        return raw_property_value_from_tsv


def _get_array_properties(kind_of_item: Optional[str] = None) -> Set[str]:
    node_array_properties = {property_name for property_name, property_info in PROPERTIES_LOOKUP["nodes"].items()
                             if property_info["type"] is list}
    edge_array_properties = {property_name for property_name, property_info in PROPERTIES_LOOKUP["edges"].items()
                             if property_info["type"] is list}
    if kind_of_item and kind_of_item.startswith("node"):
        return node_array_properties
    elif kind_of_item and kind_of_item.startswith("edge"):
        return edge_array_properties
    else:
        return node_array_properties.union(edge_array_properties)


def _get_lite_properties(kind_of_item: Optional[str] = None) -> Set[str]:
    node_lite_properties = {property_name for property_name, property_info in PROPERTIES_LOOKUP["nodes"].items()
                            if property_info["in_kg2c_lite"]}
    edge_lite_properties = {property_name for property_name, property_info in PROPERTIES_LOOKUP["edges"].items()
                            if property_info["in_kg2c_lite"]}
    if kind_of_item and kind_of_item.startswith("node"):
        return node_lite_properties
    elif kind_of_item and kind_of_item.startswith("edge"):
        return edge_lite_properties
    else:
        return node_lite_properties.union(edge_lite_properties)


def _get_kg2pre_properties(kind_of_item: Optional[str] = None) -> Set[str]:
    node_kg2pre_properties = {property_name for property_name, property_info in PROPERTIES_LOOKUP["nodes"].items()
                              if property_info["in_kg2pre"]}
    edge_kg2pre_properties = {property_name for property_name, property_info in PROPERTIES_LOOKUP["edges"].items()
                              if property_info["in_kg2pre"]}
    if kind_of_item and kind_of_item.startswith("node"):
        return node_kg2pre_properties
    elif kind_of_item and kind_of_item.startswith("edge"):
        return edge_kg2pre_properties
    else:
        return node_kg2pre_properties.union(edge_kg2pre_properties)


def _get_node_labels_property() -> str:
    labels_properties = [property_name for property_name, property_info in PROPERTIES_LOOKUP["nodes"].items()
                         if property_info.get("use_as_labels")]
    return labels_properties[0]  # Should only ever be one, so return the first item


def _get_best_description_nlp(descriptions_list: List[str]) -> Optional[str]:
    candidate_descriptions = [description for description in descriptions_list if description and len(description) < 10000]
    if len(candidate_descriptions) == 1:
        return candidate_descriptions[0]
    else:
        # Use Chunyu's NLP-based method to select the best description out of the coalesced nodes
        description_finder = select_best_description(candidate_descriptions)
        return description_finder.get_best_description


def _get_best_description_length(descriptions_list: List[str]) -> Optional[str]:
    candidate_descriptions = [description for description in descriptions_list if description and len(description) < 10000]
    if not candidate_descriptions:
        return None
    elif len(candidate_descriptions) == 1:
        return candidate_descriptions[0]
    else:
        return max(candidate_descriptions, key=len)


def _load_publications_info(publications_info_str: str, kg2_edge_id: str) -> Dict[str, any]:
    # 'publications_info' currently has a non-standard structure in KG2; keep only the PMID-organized info
    if publications_info_str.startswith("{'PMID:"):
        try:
            return ast.literal_eval(publications_info_str)
        except Exception:
            logging.warning(f"Failed to load publications_info string for edge {kg2_edge_id}.")
            with open("problem_publications_info.tsv", "a+") as problem_file:
                writer = csv.writer(problem_file, delimiter="\t")
                writer.writerow([kg2_edge_id, publications_info_str])
            return dict()
    else:
        return dict()


def _modify_column_headers_for_neo4j(plain_column_headers: List[str], file_name_root: str) -> List[str]:
    modified_headers = []
    all_array_column_names = _get_array_properties()
    for header in plain_column_headers:
        if header in all_array_column_names:
            header = f"{header}:string[]"
        elif header == 'id' and "node" in file_name_root:  # Skip setting ID for edges
            header = f"{header}:ID"
        elif header == 'node_labels':
            header = ":LABEL"
        elif header == 'subject_for_conversion':
            header = ":START_ID"
        elif header == 'object_for_conversion':
            header = ":END_ID"
        elif header == 'predicate_for_conversion':
            header = ":TYPE"
        modified_headers.append(header)
    return modified_headers


def _create_node(preferred_curie: str, name: Optional[str], category: str, all_categories: List[str],
                 expanded_categories: List[str], equivalent_curies: List[str], publications: List[str],
                 all_names: List[str], iri: Optional[str], description: Optional[str], descriptions_list: List[str]) -> Dict[str, any]:
    node_properties_lookup = PROPERTIES_LOOKUP["nodes"]
    assert isinstance(preferred_curie, node_properties_lookup["id"]["type"])
    assert isinstance(name, node_properties_lookup["name"]["type"]) or not name
    assert isinstance(category, node_properties_lookup["category"]["type"])
    assert isinstance(all_categories, node_properties_lookup["all_categories"]["type"])
    assert isinstance(expanded_categories, node_properties_lookup["expanded_categories"]["type"])
    assert isinstance(equivalent_curies, node_properties_lookup["equivalent_curies"]["type"])
    assert isinstance(publications, node_properties_lookup["publications"]["type"])
    assert isinstance(all_names, node_properties_lookup["all_names"]["type"])
    assert isinstance(iri, node_properties_lookup["iri"]["type"]) or not iri
    assert isinstance(description, node_properties_lookup["description"]["type"]) or not description
    assert isinstance(descriptions_list, list)
    return {
        "id": preferred_curie,
        "name": name,
        "category": category,
        "all_names": all_names,
        "all_categories": all_categories,
        "expanded_categories": expanded_categories,
        "iri": iri,
        "description": description,
        "descriptions_list": descriptions_list,
        "equivalent_curies": equivalent_curies,
        "publications": publications
    }


def _create_edge(subject: str, object: str, predicate: str, provided_by: List[str], publications: List[str],
                 publications_info: Dict[str, any], kg2_ids: List[str]) -> Dict[str, any]:
    edge_properties_lookup = PROPERTIES_LOOKUP["edges"]
    assert isinstance(subject, edge_properties_lookup["subject"]["type"])
    assert isinstance(object, edge_properties_lookup["object"]["type"])
    assert isinstance(predicate, edge_properties_lookup["predicate"]["type"])
    assert isinstance(provided_by, edge_properties_lookup["provided_by"]["type"])
    assert isinstance(publications, edge_properties_lookup["publications"]["type"])
    assert isinstance(publications_info, edge_properties_lookup["publications_info"]["type"])
    assert isinstance(kg2_ids, edge_properties_lookup["kg2_ids"]["type"])
    return {
        "subject": subject,
        "object": object,
        "predicate": predicate,
        "provided_by": provided_by,
        "publications": publications,
        "publications_info": publications_info,
        "kg2_ids": kg2_ids
    }


def _write_list_to_neo4j_ready_tsv(input_list: List[Dict[str, any]], file_name_root: str, is_test: bool):
    # Converts a list into the specific format Neo4j wants (string with delimiter)
    logging.info(f"  Creating {file_name_root} header file..")
    column_headers = list(input_list[0].keys())
    modified_headers = _modify_column_headers_for_neo4j(column_headers, file_name_root)
    with open(f"{KG2C_DIR}/{'test_' if is_test else ''}{file_name_root}_header.tsv", "w+") as header_file:
        dict_writer = csv.DictWriter(header_file, modified_headers, delimiter='\t')
        dict_writer.writeheader()
    logging.info(f"  Creating {file_name_root} file..")
    with open(f"{KG2C_DIR}/{'test_' if is_test else ''}{file_name_root}.tsv", "w+") as data_file:
        dict_writer = csv.DictWriter(data_file, column_headers, delimiter='\t')
        dict_writer.writerows(input_list)


def create_kg2c_json_file(canonicalized_nodes_dict: Dict[str, Dict[str, any]],
                          canonicalized_edges_dict: Dict[str, Dict[str, any]],
                          meta_info_dict: Dict[str, str], is_test: bool):
    logging.info(f" Creating KG2c JSON file..")
    kgx_format_json = {"nodes": list(canonicalized_nodes_dict.values()),
                       "edges": list(canonicalized_edges_dict.values())}
    kgx_format_json.update(meta_info_dict)
    with open(f"{KG2C_DIR}/kg2c{'_test' if is_test else ''}.json", "w+") as output_file:
        json.dump(kgx_format_json, output_file)


def create_kg2c_lite_json_file(canonicalized_nodes_dict: Dict[str, Dict[str, any]],
                               canonicalized_edges_dict: Dict[str, Dict[str, any]],
                               meta_info_dict: Dict[str, str], is_test: bool):
    logging.info(f" Creating KG2c lite JSON file..")
    # Filter out all except these properties so we create a lightweight KG
    node_lite_properties = _get_lite_properties("node")
    edge_lite_properties = _get_lite_properties("edge")
    lite_kg = {"nodes": [], "edges": []}
    for node in canonicalized_nodes_dict.values():
        lite_node = dict()
        for lite_property in node_lite_properties:
            lite_node[lite_property] = node[lite_property]
        lite_kg["nodes"].append(lite_node)
    for edge in canonicalized_edges_dict.values():
        lite_edge = dict()
        for lite_property in edge_lite_properties:
            lite_edge[lite_property] = edge[lite_property]
        lite_kg["edges"].append(lite_edge)
    lite_kg.update(meta_info_dict)

    # Save this lite KG to a JSON file
    logging.info(f"    Saving lite json...")
    with open(f"{KG2C_DIR}/kg2c_lite{'_test' if is_test else ''}.json", "w+") as output_file:
        json.dump(lite_kg, output_file)


def create_kg2c_sqlite_db(canonicalized_nodes_dict: Dict[str, Dict[str, any]],
                          canonicalized_edges_dict: Dict[str, Dict[str, any]], is_test: bool):
    logging.info(" Creating KG2c sqlite database..")
    db_name = f"kg2c{'_test' if is_test else ''}.sqlite"
    # Remove any preexisting version of this database
    if os.path.exists(db_name):
        os.remove(db_name)
    connection = sqlite3.connect(db_name)

    # Add all nodes (node object is dumped into a JSON string)
    logging.info(f"  Creating nodes table..")
    connection.execute("CREATE TABLE nodes (id TEXT, node TEXT)")
    node_rows = [(node["id"], json.dumps(node)) for node in canonicalized_nodes_dict.values()]
    connection.executemany(f"INSERT INTO nodes (id, node) VALUES (?, ?)", node_rows)
    connection.execute("CREATE UNIQUE INDEX node_id_index ON nodes (id)")
    connection.commit()
    cursor = connection.execute(f"SELECT COUNT(*) FROM nodes")
    logging.info(f"  Done creating nodes table; contains {cursor.fetchone()[0]} rows.")
    cursor.close()

    # Add all edges (edge object is dumped into a JSON string)
    logging.info(f"  Creating edges table..")
    connection.execute("CREATE TABLE edges (triple TEXT, node_pair TEXT, edge TEXT)")
    edge_rows = [(f"{edge['subject']}--{edge['predicate']}--{edge['object']}",
                  f"{edge['subject']}--{edge['object']}",
                  json.dumps(edge)) for edge in canonicalized_edges_dict.values()]
    connection.executemany(f"INSERT INTO edges (triple, node_pair, edge) VALUES (?, ?, ?)", edge_rows)
    connection.execute("CREATE UNIQUE INDEX triple_index ON edges (triple)")
    connection.execute("CREATE INDEX node_pair_index ON edges (node_pair)")
    connection.commit()
    cursor = connection.execute(f"SELECT COUNT(*) FROM edges")
    logging.info(f"  Done creating edges table; contains {cursor.fetchone()[0]} rows.")
    cursor.close()

    connection.close()


def create_kg2c_tsv_files(canonicalized_nodes_dict: Dict[str, Dict[str, any]],
                          canonicalized_edges_dict: Dict[str, Dict[str, any]],
                          biolink_version: str, is_test: bool):
    bh = BiolinkHelper(biolink_version)
    # Convert array fields into the format neo4j wants and do some final processing
    array_node_columns = _get_array_properties("node").union({"node_labels"})
    array_edge_columns = _get_array_properties("edge")
    node_labels_property = _get_node_labels_property()
    for canonicalized_node in canonicalized_nodes_dict.values():
        canonicalized_node['node_labels'] = bh.get_ancestors(canonicalized_node[node_labels_property], include_mixins=False)
        for list_node_property in array_node_columns:
            canonicalized_node[list_node_property] = _convert_list_to_string_encoded_format(canonicalized_node[list_node_property])
    for canonicalized_edge in canonicalized_edges_dict.values():
        if not is_test:  # Make sure we don't have any orphan edges
            assert canonicalized_edge['subject'] in canonicalized_nodes_dict
            assert canonicalized_edge['object'] in canonicalized_nodes_dict
        for list_edge_property in array_edge_columns:
            canonicalized_edge[list_edge_property] = _convert_list_to_string_encoded_format(canonicalized_edge[list_edge_property])
        canonicalized_edge['predicate_for_conversion'] = canonicalized_edge['predicate']
        canonicalized_edge['subject_for_conversion'] = canonicalized_edge['subject']
        canonicalized_edge['object_for_conversion'] = canonicalized_edge['object']

    # Finally dump all our nodes/edges into TSVs (formatted for neo4j)
    logging.info(f" Creating TSVs for Neo4j..")
    _write_list_to_neo4j_ready_tsv(list(canonicalized_nodes_dict.values()), "nodes_c", is_test)
    _write_list_to_neo4j_ready_tsv(list(canonicalized_edges_dict.values()), "edges_c", is_test)


def _canonicalize_nodes(neo4j_nodes: List[Dict[str, any]]) -> Tuple[Dict[str, Dict[str, any]], Dict[str, str]]:
    synonymizer = NodeSynonymizer()
    node_ids = [node.get('id') for node in neo4j_nodes if node.get('id')]
    logging.info(f"  Sending NodeSynonymizer.get_canonical_curies() {len(node_ids)} curies..")
    canonicalized_info = synonymizer.get_canonical_curies(curies=node_ids, return_all_categories=True)
    all_canonical_curies = {canonical_info['preferred_curie'] for canonical_info in canonicalized_info.values() if canonical_info}
    logging.info(f"  Sending NodeSynonymizer.get_equivalent_nodes() {len(all_canonical_curies)} curies..")
    equivalent_curies_info = synonymizer.get_equivalent_nodes(all_canonical_curies)
    recognized_curies = {curie for curie in equivalent_curies_info if equivalent_curies_info.get(curie)}
    equivalent_curies_dict = {curie: list(equivalent_curies_info.get(curie)) for curie in recognized_curies}
    with open(f"{KG2C_DIR}/equivalent_curies.pickle", "wb") as equiv_curies_dump:  # Save these for use by downstream script
        pickle.dump(equivalent_curies_dict, equiv_curies_dump, protocol=pickle.HIGHEST_PROTOCOL)
    logging.info(f"  Creating canonicalized nodes..")
    curie_map = dict()
    canonicalized_nodes = dict()
    for neo4j_node in neo4j_nodes:
        # Grab relevant info for this node and its canonical version
        canonical_info = canonicalized_info.get(neo4j_node['id'])
        canonicalized_curie = canonical_info.get('preferred_curie', neo4j_node['id']) if canonical_info else neo4j_node['id']
        publications = neo4j_node['publications'] if neo4j_node.get('publications') else []
        descriptions_list = [neo4j_node['description']] if neo4j_node.get('description') else []
        if canonicalized_curie in canonicalized_nodes:
            # Merge this node into its corresponding canonical node
            existing_canonical_node = canonicalized_nodes[canonicalized_curie]
            existing_canonical_node['publications'] = _merge_two_lists(existing_canonical_node['publications'], publications)
            existing_canonical_node['all_names'] = _merge_two_lists(existing_canonical_node['all_names'], [neo4j_node['name']])
            existing_canonical_node['descriptions_list'] = _merge_two_lists(existing_canonical_node['descriptions_list'], descriptions_list)
            # Make sure any nodes subject to #1074-like problems still appear in equivalent curies
            existing_canonical_node['equivalent_curies'] = _merge_two_lists(existing_canonical_node['equivalent_curies'], [neo4j_node['id']])
            # Add the IRI for the 'preferred' curie, if we've found that node
            if neo4j_node['id'] == canonicalized_curie:
                existing_canonical_node['iri'] = neo4j_node.get('iri')
        else:
            # Initiate the canonical node for this synonym group
            name = canonical_info['preferred_name'] if canonical_info else neo4j_node['name']
            category = canonical_info['preferred_category'] if canonical_info else neo4j_node['category']
            all_categories = list(canonical_info['all_categories']) if canonical_info else [neo4j_node['category']]
            expanded_categories = list(canonical_info['expanded_categories']) if canonical_info else [neo4j_node['category']]
            iri = neo4j_node['iri'] if neo4j_node['id'] == canonicalized_curie else None
            all_names = [neo4j_node['name']]
            canonicalized_node = _create_node(preferred_curie=canonicalized_curie,
                                              name=name,
                                              category=category,
                                              all_categories=all_categories,
                                              expanded_categories=expanded_categories,
                                              publications=publications,
                                              equivalent_curies=equivalent_curies_dict.get(canonicalized_curie, [canonicalized_curie]),
                                              iri=iri,
                                              description=None,
                                              descriptions_list=descriptions_list,
                                              all_names=all_names)
            canonicalized_nodes[canonicalized_node['id']] = canonicalized_node
        curie_map[neo4j_node['id']] = canonicalized_curie  # Record this mapping for easy lookup later
    return canonicalized_nodes, curie_map


def _canonicalize_edges(neo4j_edges: List[Dict[str, any]], curie_map: Dict[str, str], is_test: bool) -> Dict[str, Dict[str, any]]:
    canonicalized_edges = dict()
    for neo4j_edge in neo4j_edges:
        kg2_edge_id = neo4j_edge['id']
        original_subject = neo4j_edge['subject']
        original_object = neo4j_edge['object']
        if not is_test:  # Make sure we have the mappings we expect
            assert original_subject in curie_map
            assert original_object in curie_map
        canonicalized_subject = curie_map.get(original_subject, original_subject)
        canonicalized_object = curie_map.get(original_object, original_object)
        edge_publications = neo4j_edge['publications'] if neo4j_edge.get('publications') else []
        edge_provided_by = neo4j_edge['provided_by'] if neo4j_edge.get('provided_by') else []
        edge_publications_info = _load_publications_info(neo4j_edge['publications_info'], kg2_edge_id) if neo4j_edge.get('publications_info') else dict()
        if canonicalized_subject != canonicalized_object:  # Don't allow self-edges
            canonicalized_edge_key = _get_edge_key(canonicalized_subject, canonicalized_object, neo4j_edge['predicate'])
            if canonicalized_edge_key in canonicalized_edges:
                canonicalized_edge = canonicalized_edges[canonicalized_edge_key]
                canonicalized_edge['provided_by'] = _merge_two_lists(canonicalized_edge['provided_by'], edge_provided_by)
                canonicalized_edge['publications'] = _merge_two_lists(canonicalized_edge['publications'], edge_publications)
                canonicalized_edge['publications_info'].update(edge_publications_info)
                canonicalized_edge['kg2_ids'].append(kg2_edge_id)
            else:
                new_canonicalized_edge = _create_edge(subject=canonicalized_subject,
                                                      object=canonicalized_object,
                                                      predicate=neo4j_edge['predicate'],
                                                      provided_by=edge_provided_by,
                                                      publications=edge_publications,
                                                      publications_info=edge_publications_info,
                                                      kg2_ids=[kg2_edge_id])
                canonicalized_edges[canonicalized_edge_key] = new_canonicalized_edge
    return canonicalized_edges


def create_kg2c_files(is_test=False):
    """
    This function extracts all nodes/edges from the regular KG2 Neo4j endpoint (specified in your config.json),
    canonicalizes the nodes, merges edges (based on subject, object, predicate), and saves the resulting canonicalized
    graph in multiple file formats: JSON, sqlite, and TSV (ready for import into Neo4j).
    """
    # First download the proper KG2 TSV files
    local_tsv_dir_path = f"{KG2C_DIR}/kg2pre_tsvs"
    if not pathlib.Path(local_tsv_dir_path).exists():
        subprocess.check_call(["mkdir", local_tsv_dir_path])
    if not is_test:
        kg2pre_tarball_name = "kg2-tsv-for-neo4j.tar.gz"
        logging.info(f"Downloading {kg2pre_tarball_name} from the rtx-kg2 S3 bucket")
        subprocess.check_call(["aws", "s3", "cp", "--no-progress", "--region", "us-west-2", f"s3://rtx-kg2/{kg2pre_tarball_name}", KG2C_DIR])
        logging.info(f"Unpacking {kg2pre_tarball_name}..")
        subprocess.check_call(["tar", "-xvzf", kg2pre_tarball_name, "-C", local_tsv_dir_path])

    # Load the KG2pre nodes and edges into dict objects
    kg2pre_nodes = []
    kg2pre_edges = []
    nodes_tsv_path = f"{local_tsv_dir_path}/nodes.tsv"
    edges_tsv_path = f"{local_tsv_dir_path}/edges.tsv"
    logging.info(f"Loading nodes from KG2pre TSV ({nodes_tsv_path})..")
    node_headers = _get_headers(f"{local_tsv_dir_path}/nodes_header.tsv")
    edge_headers = _get_headers(f"{local_tsv_dir_path}/edges_header.tsv")
    kg2pre_node_property_names = _get_kg2pre_properties("node")
    kg2pre_edge_property_names = _get_kg2pre_properties("edge")
    with open(nodes_tsv_path) as nodes_file:
        reader = csv.reader(nodes_file, delimiter="\t")
        for row in reader:
            new_node = dict()
            for node_property_name in kg2pre_node_property_names:
                node_property_info = PROPERTIES_LOOKUP["nodes"][node_property_name]
                raw_property_value = row[node_headers.index(node_property_name)]
                new_node[node_property_name] = _load_property(raw_property_value, node_property_info["type"])
            kg2pre_nodes.append(new_node)
    logging.info(f"Loading edges from KG2pre TSV ({edges_tsv_path})..")
    with open(edges_tsv_path) as edges_file:
        reader = csv.reader(edges_file, delimiter="\t")
        for row in reader:
            new_edge = dict()
            for edge_property_name in kg2pre_edge_property_names:
                edge_property_info = PROPERTIES_LOOKUP["edges"][edge_property_name]
                raw_property_value = row[edge_headers.index(edge_property_name)]
                new_edge[edge_property_name] = _load_property(raw_property_value, edge_property_info["type"])
            kg2pre_edges.append(new_edge)

    # Do the actual canonicalization
    logging.info(f"Canonicalizing nodes..")
    canonicalized_nodes_dict, curie_map = _canonicalize_nodes(kg2pre_nodes)
    logging.info(f"Number of KG2pre nodes was reduced to {len(canonicalized_nodes_dict)} ({round((len(canonicalized_nodes_dict) / len(kg2pre_nodes)) * 100)}%)")
    logging.info(f"Canonicalizing edges..")
    canonicalized_edges_dict = _canonicalize_edges(kg2pre_edges, curie_map, is_test)
    logging.info(f"Number of KG2pre edges was reduced to {len(canonicalized_edges_dict)} ({round((len(canonicalized_edges_dict) / len(kg2pre_edges)) * 100)}%)")

    # Create a node containing information about this KG2C build
    with open(f"{KG2C_DIR}/kg2c_config.json") as config_file:
        kg2c_config_info = json.load(config_file)
    kg2_version = kg2c_config_info.get("kg2pre_version")
    biolink_version = kg2c_config_info.get("biolink_version")
    description_dict = {"kg2_version": kg2_version,
                        "biolink_version": biolink_version,
                        "build_date": datetime.now().strftime('%Y-%m-%d %H:%M')}
    description = f"{description_dict}"
    name = f"RTX-KG{kg2_version}c"
    kg2c_build_node = _create_node(preferred_curie="RTX:KG2c",
                                   name=name,
                                   all_categories=["biolink:InformationContentEntity"],
                                   expanded_categories=["biolink:InformationContentEntity"],
                                   category="biolink:InformationContentEntity",
                                   equivalent_curies=[],
                                   publications=[],
                                   iri="http://rtx.ai/identifiers#KG2c",
                                   all_names=[name],
                                   description=description,
                                   descriptions_list=[description])
    canonicalized_nodes_dict[kg2c_build_node['id']] = kg2c_build_node

    # Choose best descriptions using Chunyu's NLP-based method
    use_nlp_to_choose_descriptions = kg2c_config_info["kg2c"].get("use_nlp_to_choose_descriptions")
    node_ids = list(canonicalized_nodes_dict)
    description_lists = [canonicalized_nodes_dict[node_id]["descriptions_list"] for node_id in node_ids]
    num_cpus = os.cpu_count()
    logging.info(f" Detected {num_cpus} cpus; will use all of them to choose best descriptions")
    pool = Pool(num_cpus)
    start = time.time()
    if use_nlp_to_choose_descriptions:
        logging.info(f"Starting to use Chunyu's NLP-based method to choose best descriptions..")
        best_descriptions = pool.map(_get_best_description_nlp, description_lists)
    else:
        logging.info(f"Choosing best descriptions (longest under 10,000 characters)..")
        best_descriptions = pool.map(_get_best_description_length, description_lists)

    logging.info(f"Choosing best descriptions took {round(((time.time() - start) / 60) / 60, 2)} hours")
    # Actually decorate nodes with their 'best' description
    for num in range(len(node_ids)):
        node_id = node_ids[num]
        best_description = best_descriptions[num]
        canonicalized_nodes_dict[node_id]["description"] = best_description
        del canonicalized_nodes_dict[node_id]["descriptions_list"]
    del description_lists
    del best_descriptions
    gc.collect()

    # Do some final clean-up/formatting of nodes, now that all merging is done
    logging.info(f"Doing final clean-up/formatting of nodes")
    for node_id, node in canonicalized_nodes_dict.items():
        node["publications"] = node["publications"][:10]  # We don't need a ton of publications, so truncate them
    logging.info(f" Doing final clean-up/formatting of edges")
    # Convert our edge IDs to integers (to save space downstream) and add them as actual properties on the edges
    edge_num = 1
    for edge_id, edge in canonicalized_edges_dict.items():
        edge["id"] = edge_num
        edge_num += 1
        edge["publications"] = edge["publications"][:20]  # We don't need a ton of publications, so truncate them
        if len(edge["publications_info"]) > 20:
            pubs_info_to_remove = list(edge["publications_info"])[20:]
            for pmid in pubs_info_to_remove:
                del edge["publications_info"][pmid]

    # Actually create all of our output files (different formats for storing KG2c)
    meta_info_dict = {"kg2_version": kg2_version, "biolink_version": biolink_version}
    create_kg2c_lite_json_file(canonicalized_nodes_dict, canonicalized_edges_dict, meta_info_dict, is_test)
    create_kg2c_sqlite_db(canonicalized_nodes_dict, canonicalized_edges_dict, is_test)
    create_kg2c_tsv_files(canonicalized_nodes_dict, canonicalized_edges_dict, biolink_version, is_test)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        handlers=[logging.FileHandler("createkg2cfiles.log"),
                                  logging.StreamHandler()])
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--test', dest='test', action='store_true', default=False)
    args = arg_parser.parse_args()

    logging.info(f"Starting to create KG2canonicalized..")
    start = time.time()
    create_kg2c_files(args.test)
    logging.info(f"Done! Took {round(((time.time() - start) / 60) / 60, 2)} hours.")


if __name__ == "__main__":
    main()
