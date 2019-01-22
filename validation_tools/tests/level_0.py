# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L0 tests.
"""

#from validation_tools.utilities import validation_metadata
from pathlib import Path
import json
from urllib.request import urlopen, Request
import logging

import gdal

__author__ = 'florian girtler - girtler@geoville.com'

"""
Level 0 test no. 2: Checking the integrity of files
"""
def level_0_2(test_metadata):
    test_result = {
        'test_id': 'level_0_2',
        'test_name': 'Check integrity of files',
    }

    try:
        product_path = Path(test_metadata['validate_path'])
        inspire_file = product_path / 'inspire.xml'
        metadata = open(inspire_file).read()
        """validate metadata against INSPIRE metadata validation service"""
        host = 'http://inspire-geoportal.ec.europa.eu'
        endpoint = 'GeoportalProxyWebServices/resources/INSPIREResourceTester'

        url = '{}/{}'.format(host, endpoint)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'text/plain'
        }
        request = Request(url, data=metadata.encode("utf-8"), headers=headers)
        response = urlopen(request)

        json_data = json.loads(response.read().decode('utf-8'))

        if 'ResourceReportResource' in json_data['value']:
            test_result['result'] = {
                'finished': False,
                'passed': False,
                'Error': 'Validation failed ResourceReportResource in JSON'
            }
        elif 'PullBatchReportResource' in json_data['value']:
            test_result['result'] = {
                'finished': False,
                'passed': False,
                'Error': 'Summary validation report of multiple resources not yet implemented'
            }
        else:
            test_result['result'] = {
                'finished': True,
                'passed': True
            }
    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': ex,
        }

    return test_result


"""
Level 0 test no. 1: Checking if all required files are there
"""

def level_0_1(test_metadata):

    test_result = {
        'test_id': 'level_0_1',
        'test_name': 'Check of completeness',
    }

    try:
        missing_files = []
        unexpected_files = []
        product_path = Path(test_metadata['validate_path'])

        # check if inspire conform xml file is available
        inspire_file = product_path / 'inspire.xml'
        if not inspire_file.is_file():
            missing_files.append(inspire_file)

        """
        distinguish between netcdf and others
            - when netcdf only one file is available -> possibly check within the file?
            - when not netcdf then a metadata json file should be available?
        """
        if not test_metadata['image_format'].lower() == 'netcdf':
            required_file_prefixes = validation_metadata.get_required_file_prefixes(test_metadata)

            # go through each subdirectory (tile) of the product and check if there are all required files
            for subdir in product_path.iterdir():
                if subdir.is_dir():
                    found_required_prefixes = []
                    found_required_files = []

                    available_files = [x.name for x in subdir.iterdir() if not x.is_dir()]

                    # go through all required file prefixes and check if according files are available in the current subdir
                    for rf in required_file_prefixes:
                        for af in available_files:
                            if af.startswith(rf):
                                found_required_prefixes.append(rf)
                                found_required_files.append(af)

                    missing = set(required_file_prefixes) - set(found_required_prefixes)
                    for m in missing:
                        missing_files.append('{}/{}...'.format(subdir.name, m))

                    unexpected = set(available_files) - set(found_required_files)
                    for u in unexpected:
                        unexpected_files.append('{}/{}'.format(subdir.name, u))

        else:
            # TODO: possibly check content within the nc file?
            # check if netcdf file is available in each subdir (tile?)
            for subdir in product_path.iterdir():
                if subdir.is_dir():
                    found_netcdf_files = []

                    available_files = [x.name for x in subdir.iterdir() if not x.is_dir()]

                    # go through all available files and check netcdf files are available in the current subdir
                    for af in available_files:
                        if af.endswith('.nc'):
                            found_netcdf_files.append(af)

                    if len(found_netcdf_files) < 1:
                        missing_files.append('{}/...nc'.format(subdir.name))

                    unexpected = set(available_files) - set(found_netcdf_files)
                    for u in unexpected:
                        unexpected_files.append('{}/{}'.format(subdir.name, u))


        # fill test result
        test_passed = True
        if len(missing_files) > 0:
            test_passed = False
            test_result['missing_files'] = missing_files
        if len(unexpected_files) > 0:
            test_result['unexpected_files'] = unexpected_files

        test_result['result'] = {
            'finished': True,
            'passed': test_passed
        }

    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': ex,
        }

    return test_result
