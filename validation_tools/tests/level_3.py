# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L2 tests. L2 checks for similarity of products
"""

import os
import json


__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def level_3_1_analysis(lev3_1_tile_results, refSourceProdList, valSourceProdList):

    if len(refSourceProdList) - len(valSourceProdList) > 0:
        difference_analysis = 'Reference product has ' + str(abs(len(refSourceProdList) - len(valSourceProdList))) + \
                              ' additional products compared to validation product'
    else:
        difference_analysis = 'Validation product has ' + str(abs(len(refSourceProdList) - len(valSourceProdList))) + \
                              ' additional products compared to reference product'

    lev3_1_tile_results['metadata'] = {
        'test_level': 'L3.1',
        'passed': False,
        'summary': 'Difference in number of input products',
        'difference': difference_analysis,
        'count_ref_prod': str(len(refSourceProdList)),
        'count_val_prod': str(len(valSourceProdList)),

    }
    return lev3_1_tile_results

def level_3_1(test_metadata, comparable, name_sub_string):
    """
    Level 3 test no. 1: Compare number of input products to mosaicking
    """
    test_result = {
        'test_id': 'level_3_1',
        'test_name': 'Compare number of input products to mosaicking',
    }

    if comparable:
        lev3_1_tile_results = {}
        lev2_1_results = {}
        try:
            valPath = test_metadata['validate_path']
            refPath = test_metadata['reference_path']

            # get subdirs names
            valSubPaths = [f.path for f in os.scandir(valPath) if f.is_dir()]
            refSubPaths = [f.path for f in os.scandir(refPath) if f.is_dir()]

            test_sum = 0

            # loop over tiles if any
            for i in range(len(valSubPaths)):
                valSubPath = valSubPaths[i]
                tiled_prod = False
                if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                    if len(valSubPath.split('\\')[-1]) != 5:
                        continue
                    else:
                        tiled_prod = True
                refSubPath = refSubPaths[i]
                if tiled_prod:
                    print('Validating tile: ' + valSubPath.split('\\')[-1])

                # get json filename
                if tiled_prod:
                    valFile = valSubPath + '\\' + 'metadata' + name_sub_string + valSubPath.split('\\')[-1] + '.' + \
                              'json'
                    refFile = refSubPath + '\\' + 'metadata' + name_sub_string + valSubPath.split('\\')[-1] + '.' + \
                              'json'
                else:
                    valFile = valSubPath + '\\' + 'metadata' + name_sub_string + test_metadata['order_name'] + '.' + \
                              'json'
                    refFile = refSubPath + '\\' + 'metadata' + name_sub_string + test_metadata['order_name'] + '.' + \
                              'json'

                with open(str(valFile), 'r') as odf:
                    valJson = json.load(odf)
                with open(str(refFile), 'r') as odf:
                    refJson = json.load(odf)

                valSourceProdDict = valJson['Source_product_list']
                refSourceProdDict = refJson['Source_product_list']

                valSourceProdList = valSourceProdDict.values()
                refSourceProdList = refSourceProdDict.values()

                if len(valSourceProdDict) == len(refSourceProdDict):
                    test_sum += 0
                else:
                    lev3_1_tile_results = level_3_1_analysis(lev3_1_tile_results, refSourceProdList, valSourceProdList)
                    tile_name = valSubPath.split('\\')[-1]
                    lev2_1_results[tile_name] = {
                        'level_2_1_details': lev3_1_tile_results
                    }
                    test_sum += 1

            if test_sum == 0:
                # fill test result
                test_passed = True
                # TODO: check if test was passed
            else:
                test_passed = False

            test_result['status'] = {
                'finished': True,
                'passed': test_passed,
            }
            test_result['results'] = lev2_1_results

        except Exception as ex:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'error': ex,
            }
    else:
        print('L2.1 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

    return test_result
