# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L2 tests. L2 checks for similarity of products
"""

import os
import glob
import gdal
import numpy as np
from pathlib import Path

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def level_2_1(test_metadata, comparable, band_dict):
    """
    Level 2 test no. 1: Spatial difference of SR for all bands
    """
    print(test_metadata)

    test_result = {
        'test_id': 'level_2_1',
        'test_name': 'Spatial difference of SR for all bands',
    }
    if comparable:
        try:
            # TODO: do test
            if test_metadata['image_format'] == 'NETCDF':
                # TODO: implement xarray analysis
                driver_name = ''
                file_ext = 'nc'
            elif test_metadata['image_format'] == 'GEO_TIFF':
                driver_name = 'GTiff'
                file_ext = 'tiff'
            else:
                driver_name = 'JP2OpenJPEG'
                file_ext = 'jp2'
            if test_metadata['image_format'] == 'GEO_TIFF' or test_metadata['image_format'] == 'JP2':
                driver = gdal.GetDriverByName(driver_name)
                driver.Register()

                valPath = test_metadata['validate_path']
                refPath = test_metadata['reference_path']

                #get subdirs names
                valSubPaths = [f.path for f in os.scandir(valPath) if f.is_dir()]
                refSubPaths = [f.path for f in os.scandir(refPath) if f.is_dir()]

                # loop over tiles if any
                for i in range(len(valSubPaths)):
                    valSubPath = valSubPaths[i]
                    refSubPath = refSubPaths[i]
                    valBands = glob.glob(valSubPath + '\*.' + file_ext)
                    refBands = glob.glob(refSubPath + '\*.' + file_ext)

                    #loop over bands
                    for k in range(len(valBands)):
                        valData = gdal.Open(valBands[k])
                        refData = gdal.Open(refBands[k])
                        valRaster = valData.GetRasterBand(1)
                        refRaster = refData.GetRasterBand(1)
                        valRasterAr = valRaster.ReadAsArray()
                        refRasterAr = refRaster.ReadAsArray()
                        difRasterAr = valRasterAr - refRasterAr
                        test_sum =+ np.sum(difRasterAr)
                        print(np.sum(difRasterAr))
            else:
                #Todo: implement tests for NetCDF
                print('Implementation for NetCDF still missing')
                test_sum = -1
            if test_sum == 0:
                # fill test result
                test_passed = True
                # TODO: check if test was passed
            else:
                test_passed = False

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
    else:
        print('L2.1 test could not be executed. Products have different request parameters and thus can not be compared')

    return test_result

def level_2_2(test_metadata):
    """
    Level 2 test no. 2: Distribution of SR values for both products
    """
    test_result = {
        'test_id': 'level_2_2',
        'test_name': 'Distribution of SR values for both products',
    }

    try:
        # TODO: do test

        # fill test result
        test_passed = True
        # TODO: check if test was passed

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

def level_2_3(test_metadata):
    """
    Level 2 test no. 3: Distribution of scene classification
    """
    test_result = {
        'test_id': 'level_2_3',
        'test_name': 'Distribution of scene classification',
    }

    try:
        # TODO: do test

        # fill test result
        test_passed = True
        # TODO: check if test was passed

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

def level_2_4(test_metadata):
    """
    Level 2 test no. 4: Distribution of source_index
    """
    test_result = {
        'test_id': 'level_2_4',
        'test_name': 'Distribution of source_index',
    }

    try:
        # TODO: do test

        # fill test result
        test_passed = True
        # TODO: check if test was passed

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