# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate validation of s2gm products.
"""

import os
import logging
import argparse
from datetime import datetime, date

__author__ = 'jan wevers, tanja gasber & florian girtler - jan.wevers@brockmann-consult.de, gasber@geoville.com, girtler@geoville.com'

def log_inputs(tests, reference_path, validate_path):
    if not os.path.isdir('./logs'):
        os.makedirs('./logs')
    try:
        logging.basicConfig(filename='./logs/execution.log', filemode='a',level=logging.DEBUG)
    except FileNotFoundError:
        print('log file does not exist and will be created')
        f = open('./logs/execution.log')
        f.close()
        logging.basicConfig(filename='./logs/execution.log', filemode='a', level=logging.DEBUG)
    logging.info('ValidationOp executed: %s', str(datetime.now()))
    logging.debug('Requested tests by the user: %s', str(tests))
    logging.debug('Reference: {}, to validate: {}'.format(reference_path, validate_path))


def check_input(reference_path, validate_path):
    #TODO: see if all pkl files exist for both reference and to-validate directory
    #TODO: check if data are valid (e.g. reference is older than to-validate)
    return True


def prepare_tests(tests, reference_path, validate_path):
    log_inputs(tests, reference_path, validate_path)

    #TODO: check integrity of reference and validation folder
    if (not check_input(reference_path, validate_path)):
        logging.error('Input data are not valid, check log for more information.')
        return
    #TODO: run the different checks
    if 'L0' in tests:
        print('running test L0 for {}'.format(validate_path))
        # L0: check file integrity of validate folder
        #result = run_L0_test(validate_path)
    if 'L1' in tests:
        print('running test L1 for {}'.format(validate_path))


    #TODO: create validation report




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
        nargs=1,
        type=str,
        required=True,
        metavar="path",
        help='Path to the directory of the validation reference data'
    )
    CLI.add_argument(
        "-v",
        "--validate",
        nargs=1,
        type=str,
        required=True,
        metavar="path",
        help='Path to the directory of the data to be validated'
    )
    args = CLI.parse_args()
    prepare_tests(args.tests, args.reference, args.validate)