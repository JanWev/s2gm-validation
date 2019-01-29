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
from validation_tools.utilities.static_validation_parameters import refl_bands_dict, aux_band_dict, period_dict, \
    res_dict

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

    # extract all metadata from the validation.json file from validation dataset
    # these data are required to do the validation
    try:
        val_order_data_file = Path(validate_path) / 'validation.json'
        with open(str(val_order_data_file), 'r') as odf:
            val_order_data = json.load(odf)

    except Exception as ex:
        logging.error('Reading of validation order data from JSON file failed: {}'.format(ex))
        raise Exception('Reading of validation order data from JSON file failed: {}'.format(ex))

    for key, value in val_order_data.items():
        test_metadata[key] = value

    # extract all metadata from the validation.json file from reference dataset
    # these data are required to check equality of validation and reference data
    try:
        ref_order_data_file = Path(reference_path) / 'validation.json'
        with open(str(ref_order_data_file), 'r') as odf:
            ref_order_data = json.load(odf)

    except Exception as ex:
        logging.error('Reading of validation order data from JSON file failed: {}'.format(ex))
        raise Exception('Reading of validation order data from JSON file failed: {}'.format(ex))

    # Todo: compare order data of validation and ref dataset

    if not len(val_order_data) == len(ref_order_data):
        logging.error('Reference and validation validation.json have different length. One of two files must be corrupt')
        raise Exception('Reference and validation validation.json have different length. One of two files must be corrupt')
    else: #compare the two files
        if val_order_data == ref_order_data:
            comparable = True
        else:
            comparable = False
            for item in ref_order_data:
                if not isinstance(ref_order_data[item], str):
                    ref_item = str(ref_order_data[item])
                    val_item = str(val_order_data[item])
                else:
                    ref_item = ref_order_data[item]
                    val_item = val_order_data[item]
                if ref_item != val_item:
                    print('DIFFERENCE - ' + item + ':' + ref_item + ' != ' + val_item)
        # logging.debug('Reference data and validation data have different ')

    # TODO: possibly see if all metadata exist for mosaic to validate (and reference if provided): json file @flo: what do you mean? (jan)
    return test_metadata, comparable


def run_tests(tests, test_metadata, comparable, refl_bands_dict, aux_band_dict):

    test_results = {}

    val_res_path = test_metadata['validate_path'] + '\\val_res'
    if not os.path.isdir(val_res_path):
        os.makedirs(val_res_path)


    #run the different validation tests

    if 'L0' in tests:
        logging.info('running test L0 for {}'.format(test_metadata['validate_path']))
        # L0: check file integrity of validate folder
        #result = run_L0_test(validate_path)

        print('Started L0.1 tests')
        test_results['level_0_1'] = level_0.level_0_1(test_metadata)
        print('Finished L0.1 tests')

        print('Started L0.2 tests')
        test_results['level_0_2'] = level_0.level_0_2(test_metadata)
        print('Finished L0.2 tests')

    if 'L1' in tests:
        logging.info('running test L1 for {}'.format(test_metadata))

    if 'L2' in tests:
        #create name substring
        name_sub_string = '_' + period_dict[test_metadata['compositing_period']] + \
                          res_dict[test_metadata['resolution']] + '_' + \
                          test_metadata['mosaic_start_date'].replace('-','') + '_'

        logging.info('running test L2 for {}'.format(test_metadata))

        print('Started L2.1 tests')
        # Todo: Include counts and percentage for changed SR pixels & NoData (How many of all pixels are affected)
        test_results['level_2_1'] = level_2.level_2_1(
            test_metadata, comparable, refl_bands_dict, name_sub_string)
        print('Finished L2.1 tests')

        print('Start L2.2 tests')
        test_results['level_2_2'] = level_2.level_2_2(
            test_metadata, comparable, refl_bands_dict, name_sub_string)
        print('Finished L2.2 tests')

        print('Start L2.3 tests')
        # Todo: Include counts and percentage for changed scene classification pix (How many of all pixels are affected)
        test_results['level_2_3'] = level_2.level_2_3(
            test_metadata, comparable, aux_band_dict, name_sub_string, val_res_path)
        print('Finished L2.3 tests')

    if 'L3' in tests:
        logging.info('running test L3 for {}'.format(test_metadata))

    return test_results, val_res_path




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
        test_metadata, comparable = prepare_tests(args.tests, args.validate, args.reference)
    except Exception as ex:
        logging.error('Preparing of test failed: {}'.format(ex))
        print('Preparing of test failed: {}'.format(ex))
        sys.exit(1)

    test_results, val_res_path = run_tests(args.tests, test_metadata, comparable, refl_bands_dict, aux_band_dict)

    # dump resulst to json
    with open(val_res_path + '/validation_report.json', 'w') as outfile:
        json.dump(test_results, outfile)

    # TODO: create better validation report
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(test_results)

