#!/bin/env python3
"""
This script creates a canonicalized version of KG2 stored in various file formats, including TSVs ready for import
into Neo4j. Files are created in the directory this script is in. It relies on the options you specify in
kg2c_config.json; in particular, the KG2c will be built off of the KG2 endpoint you specify in that config file.
Usage: python3 build_kg2c.py [--test]
"""
import argparse
import logging
import pathlib
import json
import os
import subprocess
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from create_kg2c_files import create_kg2c_files
from record_kg2c_meta_info import record_meta_kg_info
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../")  # code directory
from RTXConfiguration import RTXConfiguration

KG2C_DIR = f"{os.path.dirname(os.path.abspath(__file__))}"
CODE_DIR = f"{KG2C_DIR}/.."
RTX_CONFIG = RTXConfiguration()


def _setup_config_dbs_file(kg2pre_neo4j_endpoint: str, synonymizer_name: str):
    """
    This function locally modifies config_dbs.json to point to the right KG2pre Neo4j and synonymizer.
    """
    logging.info("Creating a config_dbs.json file pointed to the right synonymizer and KG2pre Neo4j..")
    config_dbs_file_path = f"{CODE_DIR}/config_dbs.json"

    # Save a copy of any pre-existing config_dbs.json so we don't overwrite it
    original_config_dbs_file = pathlib.Path(config_dbs_file_path)
    if original_config_dbs_file.exists():
        subprocess.check_call(["mv", config_dbs_file_path, f"{config_dbs_file_path}_KG2CBUILDTEMP"])
        subprocess.check_call(["cp", f"{config_dbs_file_path}_KG2CBUILDTEMP", config_dbs_file_path])

    RTXConfiguration()  # Regenerates config_secrets.json with the latest version
    with open(config_dbs_file_path) as config_dbs_file:
        rtx_config_dbs_dict = json.load(config_dbs_file)
    # Point to the 'right' KG2 Neo4j (the one specified in the KG2c config) and synonymizer (we always use simple name)
    rtx_config_dbs_dict["neo4j"]["KG2pre"] = kg2pre_neo4j_endpoint
    rtx_config_dbs_dict["database_downloads"]["node_synonymizer"] = f"/something/{synonymizer_name}"  # Only need name, not full path

    # Save our new config_dbs.json file
    with open(config_dbs_file_path, "w+") as revised_config_dbs_file:
        json.dump(rtx_config_dbs_dict, revised_config_dbs_file)


def _upload_output_files_to_s3():
    logging.info("Uploading KG2c json and TSV files to S3..")
    tarball_path = f"{KG2C_DIR}/kg2c-tsv.tar.gz"
    json_lite_file_path = f"{KG2C_DIR}/kg2c_lite.json"
    subprocess.check_call(["tar", "-czvf", tarball_path, "nodes_c.tsv", "nodes_c_header.tsv", "edges_c.tsv", "edges_c_header.tsv"])
    subprocess.check_call(["aws", "s3", "cp", "--no-progress", "--region", "us-west-2", tarball_path, "s3://rtx-kg2/"])
    subprocess.check_call(["gzip", "-f", json_lite_file_path])
    subprocess.check_call(["aws", "s3", "cp", "--no-progress", "--region", "us-west-2", f"{json_lite_file_path}.gz", "s3://rtx-kg2/"])


def _create_kg2pre_tsv_test_files():
    # Download the full KG2pre TSVs (since no test versions are available)
    kg2pre_tarball_name = "kg2-tsv-for-neo4j.tar.gz"
    logging.info(f"Downloading {kg2pre_tarball_name} from the rtx-kg2 S3 bucket")
    subprocess.check_call(
        ["aws", "s3", "cp", "--no-progress", "--region", "us-west-2", f"s3://rtx-kg2/{kg2pre_tarball_name}", KG2C_DIR])
    logging.info(f"Unpacking {kg2pre_tarball_name}..")
    local_tsv_dir_path = f"{KG2C_DIR}/kg2pre_tsvs"
    subprocess.check_call(["tar", "-xvzf", kg2pre_tarball_name, "-C", local_tsv_dir_path])

    # Reduce the files to include only N nodes and edges
    local_nodes_path = f"{local_tsv_dir_path}/nodes.tsv"
    local_nodes_path_temp = f"{local_tsv_dir_path}/nodes.tsv_TEMP"
    local_edges_path = f"{local_tsv_dir_path}/edges.tsv"
    local_edges_path_temp = f"{local_tsv_dir_path}/edges.tsv_TEMP"
    # Note: using the LAST N edges means the KG2pre build node should be included (usually last node in TSVs)
    subprocess.check_call(["tail", "-100000", local_nodes_path, ">", local_nodes_path_temp])
    subprocess.check_call(["mv", local_nodes_path_temp, local_nodes_path])
    subprocess.check_call(["tail", "-100000", local_edges_path, ">", local_edges_path_temp])
    subprocess.check_call(["mv", local_edges_path_temp, local_edges_path])


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        handlers=[logging.FileHandler("build.log"),
                                  logging.StreamHandler()])
    start = time.time()
    # Grab any parameters passed to this script
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--test", dest="test", action='store_true', default=False)
    args = arg_parser.parse_args()
    logging.info(f"STARTING {'TEST ' if args.test else ''}KG2c BUILD")

    # Load the KG2c config file
    with open(f"{KG2C_DIR}/kg2c_config.json") as config_file:
        kg2c_config_info = json.load(config_file)
    kg2_version = kg2c_config_info["kg2pre_version"]
    kg2pre_endpoint = kg2c_config_info["kg2pre_neo4j_endpoint"]
    biolink_version = kg2c_config_info["biolink_version"]
    build_kg2c = kg2c_config_info["kg2c"]["build"]
    upload_to_s3 = kg2c_config_info["kg2c"]["upload_to_s3"]
    use_local_kg2pre_tsvs = kg2c_config_info["kg2c"].get("use_local_kg2pre_tsvs")
    build_synonymizer = kg2c_config_info["synonymizer"]["build"]
    synonymizer_name = kg2c_config_info["synonymizer"]["name"]
    upload_to_arax_databases_rtx_ai = kg2c_config_info["upload_to_arax_databases.rtx.ai"]
    upload_directory = kg2c_config_info["upload_directory"]
    logging.info(f"KG2pre version to use is {kg2_version}")
    logging.info(f"KG2pre neo4j endpoint to use is {kg2pre_endpoint}")
    logging.info(f"Biolink model version to use is {biolink_version}")
    logging.info(f"Synonymizer to use is {synonymizer_name}")
    arax_synonymizer_dir = f"{CODE_DIR}/ARAX/NodeSynonymizer"
    synonymizer_file = pathlib.Path(f"{arax_synonymizer_dir}/{synonymizer_name}")

    # Make sure synonymizer settings are valid
    if build_synonymizer:
        if not synonymizer_name:
            raise ValueError(f"You must specify the name to give the new synonymizer in kg2c_config.json.")
        if upload_to_arax_databases_rtx_ai and not upload_directory:
            raise ValueError(f"You must specify the path of the directory on arax.ncats.io to upload synonymizer "
                             f"artifacts to in kg2c_config.json.")
    else:
        if not synonymizer_name:
            raise ValueError(f"You must specify the name of the synonymizer to use in kg2c_config.json since you are "
                             f"not building a new synonymizer.")
        elif not synonymizer_file.exists():
            raise ValueError(f"The synonymizer specified in kg2c_config.json does not exist in {arax_synonymizer_dir}. "
                             f"You must put a copy of it there, use a different synonymizer, or opt to build a "
                             f"new synonymizer in kg2c_config.json.")

    # Set up an RTX config_local.json file that points to the right KG2 and synonymizer
    _setup_config_dbs_file(kg2pre_endpoint, synonymizer_name)

    # Create KG2pre test TSV files as applicable
    if args.test and not use_local_kg2pre_tsvs:
        _create_kg2pre_tsv_test_files()

    # Build a new node synonymizer, if we're supposed to
    if build_synonymizer:
        logging.info("Building node synonymizer off of specified KG2..")
        subprocess.check_call(["python3", f"{KG2C_DIR}/synonymizer_build/build_synonymizer.py",
                               kg2_version, "--useconfigname"] + (["--downloadkg2pre"] if not args.test else []))

        logging.info(f"Regenerating autocomplete database..")
        subprocess.check_call(["python3", f"{KG2C_DIR}/synonymizer_build/dump_autocomplete_node_info.py", kg2_version])
        subprocess.check_call(["python3", f"{CODE_DIR}/autocomplete/create_load_db.py",
                               "--input", f"{KG2C_DIR}/synonymizer_build/autocomplete_node_info.tsv",
                               "--output" f"{KG2C_DIR}/synonymizer_build/autocomplete.sqlite"])

        if upload_to_arax_databases_rtx_ai:
            logging.info(f"Uploading synonymizer artifacts to arax-databases.rtx.ai:{upload_directory}")
            subprocess.check_call(["bash", "-x", f"{KG2C_DIR}/upload-synonymizer-artifacts.sh", RTX_CONFIG.db_host,
                                   upload_directory, synonymizer_name])

        # Move the new synonymizer into the ARAX NodeSynonymizer directory so it can be queried properly
        logging.info(f"Moving the new synonymizer into the ARAX NodeSynonymizer directory")
        subprocess.check_call(["mv", f"{KG2C_DIR}/synonymizer_build/{synonymizer_name}",
                               f"{arax_synonymizer_dir}/{synonymizer_name}"])

        logging.info("Done building synonymizer.")

    if build_kg2c:
        # Actually build KG2c
        logging.info("Calling create_kg2c_files.py..")
        create_kg2c_files(args.test)
        logging.info("Calling record_kg2c_meta_info.py..")
        record_meta_kg_info(args.test)

        # Upload artifacts to the relevant places (done even for test builds, to ensure these processes work)
        if upload_to_arax_databases_rtx_ai:
            logging.info(f"Uploading KG2c artifacts to arax-databases.rtx.ai:{upload_directory}")
            subprocess.check_call(["bash", "-x", f"{KG2C_DIR}/upload-kg2c-artifacts.sh", RTX_CONFIG.db_host,
                                   upload_directory])
        if upload_to_s3:
            _upload_output_files_to_s3()

        logging.info(f"DONE WITH {'TEST ' if args.test else ''}KG2c BUILD! Took {round(((time.time() - start) / 60) / 60, 1)} hours")

    # Undo the revisions we made to config_dbs.json
    config_dbs_file_path = f"{CODE_DIR}/config_dbs.json"
    temp_config_dbs_file_path = f"{config_dbs_file_path}_KG2CBUILDTEMP"
    temp_config_dbs_path = pathlib.Path(temp_config_dbs_file_path)
    if temp_config_dbs_path.exists():
        subprocess.check_call(["mv", temp_config_dbs_file_path, config_dbs_file_path])


if __name__ == "__main__":
    main()
