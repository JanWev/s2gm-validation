# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L2 tests. L2 checks for similarity of products
"""

import os
import glob
import gdal
import numpy as np
import matplotlib.pyplot as plt
# import xarray as xr
import netCDF4
from collections import Counter

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def plot_histogram(d):
    # An "interface" to matplotlib.axes.Axes.hist() method
    n, bins, patches = plt.hist(x=d, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('My Very Own Histogram')
    plt.text(23, 45, r'$\mu=15, b=3$')
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)

def level_2_1(test_metadata, comparable, refl_bands_dict, aux_band_dict, name_sub_string):
    """
    Level 2 test no. 1: Spatial difference of SR for all bands
    """
    print(test_metadata)

    test_result = {
        'test_id': 'level_2_1',
        'test_name': 'Spatial difference of SR for all bands',
    }
    if comparable:
        test_result_info = []
        try:
            if test_metadata['image_format'] == 'NETCDF':
                driver_name = ''
                file_ext = 'nc'
            elif test_metadata['image_format'] == 'GEO_TIFF':
                driver_name = 'GTiff'
                file_ext = 'tiff'
            else:
                driver_name = 'JP2OpenJPEG'
                file_ext = 'jp2'
            if test_metadata['image_format'] == 'GEO_TIFF' or test_metadata['image_format'] == 'JP2':
                test_sum = 0
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

                    #loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band in list(refl_bands_dict.keys()):
                            valBand = valSubPath + '\\' + band + name_sub_string + test_metadata['order_name'] + '.' + \
                                      file_ext
                            refBand = refSubPath + '\\' + band + name_sub_string + test_metadata['order_name'] + '.' + \
                                      file_ext
                            valData = gdal.Open(valBand)
                            refData = gdal.Open(refBand)
                            valRaster = valData.GetRasterBand(1)
                            refRaster = refData.GetRasterBand(1)
                            valRasterAr = valRaster.ReadAsArray()
                            refRasterAr = refRaster.ReadAsArray()
                            difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float)).flatten()

                            # Todo: define thresholds and plots for differnces
                            test_sum += np.sum(difRasterAr)
                            if np.sum(difRasterAr) != 0:
                                test_result_info.append(
                                    'Test for band ' + band + 'showed difference. Sum of difference: ' + str(
                                        np.sum(difRasterAr)))
                            else:
                                test_result_info.append(
                                    'Test for band ' + band + 'showed no difference. Bands are equal.')

                print('End of reflectance tests.')

            else:
                print('Started implementation for NetCDF')
                test_sum = 0
                valPath = test_metadata['validate_path']
                refPath = test_metadata['reference_path']

                # get subdirs names
                valSubPaths = [f.path for f in os.scandir(valPath) if f.is_dir()]
                refSubPaths = [f.path for f in os.scandir(refPath) if f.is_dir()]

                # loop over tiles if any
                for i in range(len(valSubPaths)):
                    valSubPath = valSubPaths[i]
                    refSubPath = refSubPaths[i]
                    valNetcdfFile = glob.glob(valSubPath + '\*.' + file_ext)[0]
                    refNetcdfFile = glob.glob(refSubPath + '\*.' + file_ext)[0]

                    #xarray solution currently not working due to false data type (_Unsigned) in products
                    # valDataset = xr.open_dataset(valNetcdfFile)
                    # refDataset = xr.open_dataset(refNetcdfFile)
                    # valdf = valDataset.to_dataframe()
                    # refdf = refDataset.to_dataframe()

                    valNetcdf = netCDF4.Dataset(valNetcdfFile, 'r')
                    refNetcdf = netCDF4.Dataset(refNetcdfFile, 'r')

                    # loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band in list(refl_bands_dict.keys()):
                            valData = valNetcdf.variables[band][:,:]
                            refData = refNetcdf.variables[band][:,:]
                            valRasterAr = np.ma.filled(valData)
                            refRasterAr = np.ma.filled(refData)
                            difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float)).flatten()
                            test_sum += np.sum(difRasterAr)
                            if np.sum(difRasterAr) != 0:
                                test_result_info.append(
                                    'Test for band ' + band + 'showed difference. Sum of difference: ' + str(
                                        np.sum(difRasterAr)))
                            else:
                                test_result_info.append(
                                    'Test for band ' + band + 'showed no difference. Bands are equal.')


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
        print('L2.1 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

    return test_result, test_result_info

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