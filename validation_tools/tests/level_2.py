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

def level_2_1_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_results, band):
    # check SR only no NoData values. Mask NoData
    valRasterAr = np.ma.masked_where(valRasterAr == 65535, valRasterAr)
    refRasterAr = np.ma.masked_where(refRasterAr == 65535, refRasterAr)
    difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float)).flatten()
    # Todo: define thresholds and plots for differnces

    # calc statistics
    band_sum = np.ma.sum(difRasterAr)

    test_sum += band_sum

    if np.sum(difRasterAr) != 0:
        lev2_1_results[band] = {
            'test_level': 'L2.1',
            'passed': False,
            'summary': 'Test for band ' + band + ' showed differences.',
            'difference': str(band_sum),
        }
    return lev2_1_results, test_sum

def level_2_1_evaluation(lev2_1_results, bands):
    if len(lev2_1_results) == len(bands):
        affected_bands = 'All'
    if len(lev2_1_results) == 1:
        affected_bands = 'One'
    else:
        affected_bands ='Some'

    return affected_bands

def level_2_1(test_metadata, comparable, refl_bands_dict, aux_band_dict, name_sub_string):
    """
    Level 2 test no. 1: Spatial difference of SR for all bands
    """
    test_result = {
        'test_id': 'level_2_1',
        'test_name': 'Spatial difference of SR for all bands',
    }
    if comparable:
        lev2_1_results = {}
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
                            lev2_1_results, test_sum = level_2_1_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_results,
                                                                band)
                affected_bands = level_2_1_evaluation(lev2_1_results, test_metadata['bands'])

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
                            lev2_1_results = level_2_1_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_results,
                                                                band)
                affected_bands, test_sum = level_2_1_evaluation(lev2_1_results, test_metadata['bands'])

            if test_sum == 0:
                # fill test result
                test_passed = True
                # TODO: check if test was passed
            else:
                test_passed = False

            test_result['result'] = {
                'finished': True,
                'passed': test_passed,
            }
            test_result['affected_bands'] = affected_bands
            test_result['level_2_1_details'] = lev2_1_results

        except Exception as ex:
            test_result['result'] = {
                'finished': False,
                'passed': False,
                'error': ex,
            }
    else:
        print('L2.1 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

    return test_result

def level_2_2_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_results, band):
    # check SR only no NoData values. Mask NoData
    valRasterAr = np.ma.masked_where(valRasterAr == 65535, valRasterAr)
    refRasterAr = np.ma.masked_where(refRasterAr == 65535, refRasterAr)
    difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float)).flatten()
    # Todo: define thresholds and plots for differnces

    # calc statistics
    band_sum = np.ma.sum(difRasterAr)
    band_median = np.ma.median(difRasterAr)
    band_mean = np.ma.mean(difRasterAr)
    band_std = np.ma.std(difRasterAr)

    if band_mean == band_median and band_std == .0:
        issue = 'Constant shift in SR'
    else:
        issue = 'Heterogeneous change in SR. Make further checks'

    test_sum += band_sum

    if np.sum(difRasterAr) != 0:
        lev2_1_results[band] = {
            'test_level': 'L2.2',
            'passed': False,
            'summary': 'Statistics for band with differences',
            'issue': issue,
            'median': str(band_median),
            'mean': str(band_mean),
            'std': str(band_std)
        }
    return lev2_1_results, test_sum

def level_2_2(test_metadata, comparable, refl_bands_dict, aux_band_dict, name_sub_string):
    """
    Level 2 test no. 2: Distribution of SR values for both products
    """
    test_result = {
        'test_id': 'level_2_2',
        'test_name': 'Distribution of SR values for both products',
    }

    if comparable:
        lev2_1_results = {}
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
                            lev2_1_results, test_sum = level_2_2_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_results,
                                                                band)
                affected_bands = level_2_1_evaluation(lev2_1_results, test_metadata['bands'])

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
                    valNetcdf = netCDF4.Dataset(valNetcdfFile, 'r')
                    refNetcdf = netCDF4.Dataset(refNetcdfFile, 'r')

                    # loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band in list(refl_bands_dict.keys()):
                            valData = valNetcdf.variables[band][:,:]
                            refData = refNetcdf.variables[band][:,:]
                            valRasterAr = np.ma.filled(valData)
                            refRasterAr = np.ma.filled(refData)
                            lev2_1_results, test_sum = level_2_2_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_results,
                                                                band)
                affected_bands = level_2_1_evaluation(lev2_1_results, test_metadata['bands'])

            if test_sum == 0:
                # fill test result
                test_passed = True
                # TODO: check if test was passed
            else:
                test_passed = False

            test_result['result'] = {
                'finished': True,
                'passed': test_passed,
            }
            test_result['affected_bands'] = affected_bands
            test_result['level_2_2_details'] = lev2_1_results

        except Exception as ex:
            test_result['result'] = {
                'finished': False,
                'passed': False,
                'error': ex,
            }
    else:
        print('L2.1 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

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