# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate validation of s2gm products.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, date
import json
from pathlib import Path

from validation_tools.tests import level_0, level_1, level_2, level_3

import pprint
import traceback


__author__ = 'jan wevers, tanja gasber & florian girtler - jan.wevers@brockmann-consult.de, gasber@geoville.com, girtler@geoville.com'


def log_inputs(tests, reference_path, validate_path):
    if not os.path.isdir('./validation_tools/logs'):
        os.makedirs('./validation_tools/logs')
    try:
        logging.basicConfig(filename='./validation_tools/logs/execution.log', filemode='a',level=logging.DEBUG)
    except FileNotFoundError:
        print('log file does not exist and will be created')
        f = open('./validation_tools/logs/execution.log')
        f.close()
        logging.basicConfig(filename='./validation_tools/logs/execution.log', filemode='a', level=logging.DEBUG)
    logging.info('ValidationOp executed: %s', str(datetime.now()))
    logging.debug('Requested tests by the user: %s', str(tests))
    logging.debug('Reference: {}, to validate: {}'.format(reference_path, validate_path))

"""
This function tries to read the metadata required for the validation. 
The main source for these data is the file 'order_data.json' that has
to be available in the root directory of the product that should be 
validated.

If the file was not generated, it can be created manually according to
the example in the README.
"""
def prepare_tests(tests, validate_path, reference_path = None):
    log_inputs(tests, validate_path, reference_path)

    test_metadata = {
        'validate_path': validate_path,
        'reference_path': reference_path,
    }

    # extract all metadata from the order_data.json file
    # these data are required to do the validation
    try:
        order_data_file = Path(validate_path) / 'validation.json'
        with open(str(order_data_file), 'r') as odf:
            order_data = json.load(odf)

    except Exception as ex:
        logging.error('Reading of order data from JSON file failed: {}'.format(ex))
        raise Exception('Reading of order data from JSON file failed: {}'.format(ex))

    for key, value in order_data.items():
        test_metadata[key] = value

    # TODO: possibly see if all metadata exist for mosaic to validate (and reference if provided): json file

    return test_metadata


def run_tests(tests, test_metadata):

    test_results = []

    #run the different validation tests

    if 'L0' in tests:
        logging.info('running test L0 for {}'.format(test_metadata['validate_path']))
        # L0: check file integrity of validate folder
        #result = run_L0_test(validate_path)

        test_results.append(level_0.level_0_1(test_metadata))

        test_results.append(level_0.level_0_2(test_metadata))

    # TODO: run the remaining tests
    if 'L1' in tests:
        logging.info('running test L1 for {}'.format(test_metadata))

    if 'L2' in tests:
        logging.info('running test L2 for {}'.format(test_metadata))

    if 'L3' in tests:
        logging.info('running test L3 for {}'.format(test_metadata))

    return test_results




if __name__ == "__main__":
    CLI = argparse.ArgumentParser(description = "This script retrieves Sentinel-2 metadata from copernicus hub and imports it into a database")
    CLI.add_argument(
        "-t",
        "--tests",
        nargs="+",
        type=str,
        default=['L0', 'L1', 'L2', 'L3'],
        required=False,
        metavar="test-ID",
        help='IDs of tests that should be run. Can be L0, L1, L2 or L3. If omitted all available tests will be run'
    )
    CLI.add_argument(
        "-r",
        "--reference",
        type=str,
        required=False,
        metavar="path",
        help='Path to the directory of the validation reference data'
    )
    CLI.add_argument(
        "-v",
        "--validate",
        type=str,
        required=True,
        metavar="path",
        help='Path to the directory of the data to be validated'
    )
    args = CLI.parse_args()

    # check integrity of data to be validated
    try:
        test_metadata = prepare_tests(args.tests, args.validate, args.reference)
    except Exception as ex:
        logging.error('Preparing of test failed: {}'.format(ex))
        print('Preparing of test failed: {}'.format(ex))
        sys.exit(1)

    test_results = run_tests(args.tests, test_metadata)


    # TODO: create better validation report
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(test_results)

