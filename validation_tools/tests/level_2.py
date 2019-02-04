# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L2 tests. L2 checks for similarity of products
"""

import os
import glob
import gdal
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# import xarray as xr
import netCDF4
from collections import Counter

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def plot_histogram(refRasterAr, xlabel, ylabel, title, plot_file):
    sns.set(color_codes=True)
    sns.set(font_scale=1.5)
    # sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (8, 8)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.hist(refRasterAr)
    ax.set(xlabel=xlabel,
           ylabel=ylabel,
           title=title)
    plt.savefig(plot_file)
    plt.clf()
    plt.close()


def scatter_plot(refRasterAr, valRasterAr, xlabel, ylabel, title, plot_file, xlim, ylim):
    df = pd.DataFrame({'ref': refRasterAr, 'val': valRasterAr})
    h = sns.jointplot(x="val", y="ref", data=df, ylim=ylim, xlim=xlim)
    h.set_axis_labels(xlabel, ylabel, fontsize=12)
    h.fig.subplots_adjust(top=0.9)
    h.fig.suptitle(title, fontsize=12)

    plt.savefig(plot_file)
    plt.clf()
    plt.close()

def plot_refl_histogram(RasterAr, xlabel, ylabel, title, plot_file):
    RasterArFl = RasterAr.astype(float)
    RasterArFl.fill_value = np.nan
    RasterArFlFilled = RasterArFl.filled()
    RasterArFlFilled = RasterArFlFilled[~np.isnan(RasterArFlFilled)]
    RasterArFlFilled = RasterArFlFilled[RasterArFlFilled != 0]
    ax = sns.distplot(RasterArFlFilled)
    ax.set(xlabel=xlabel,
           ylabel=ylabel,
           title=title)

    plt.savefig(plot_file)
    plt.clf()
    plt.close()
    
def refl_scatter_plot(refRasterAr, valRasterAr, xlabel, ylabel, title, plot_file, xlim, ylim):
    df = pd.DataFrame({'ref': refRasterAr, 'val': valRasterAr})
    h = sns.jointplot(x="val", y="ref", data=df, ylim=ylim, xlim=xlim, joint_kws=dict(marker='o', s=2))
    h.set_axis_labels(xlabel, ylabel, fontsize=12)
    h.fig.subplots_adjust(top=0.9)
    h.fig.suptitle(title, fontsize=12)

    # plt.setp(marker='o', markersize=0.5)
    plt.savefig(plot_file)
    plt.clf()
    plt.close()

def level_2_1_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_tile_results, band):
    # check SR only no NoData values. Mask NoData
    valRasterAr = np.ma.masked_where(valRasterAr == 65535, valRasterAr).flatten()
    refRasterAr = np.ma.masked_where(refRasterAr == 65535, refRasterAr).flatten()
    difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float))
    # Todo: define thresholds and plots for differnces

    # calc statistics
    band_sum = np.ma.sum(difRasterAr)

    test_sum += band_sum

    if np.sum(difRasterAr) != 0:
        test_sum += band_sum
        lev2_1_tile_results[band] = {
            'test_level': 'L2.1',
            'passed': False,
            'summary': 'Test for band ' + band + ' showed differences.',
            'difference': str(band_sum),
        }
    return lev2_1_tile_results, test_sum


def level_2_1_evaluation(lev2_1_tile_results, bands):
    if len(lev2_1_tile_results) == len(bands):
        affected_bands = 'All'
    if len(lev2_1_tile_results) == 1:
        affected_bands = 'One'
    if len(lev2_1_tile_results) == 0:
        affected_bands = 'None'
    else:
        affected_bands ='Some'

    return affected_bands

def level_2_1(test_metadata, comparable, refl_bands_dict, name_sub_string):
    """
    Level 2 test no. 1: Spatial difference of SR for all bands
    """
    test_result = {
        'test_id': 'level_2_1',
        'test_name': 'Spatial difference of SR for all bands',
    }
    if comparable:
        lev2_1_tile_results = {}
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
                    tiled_prod = False
                    if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                        if len(valSubPath.split('\\')[-1]) != 5:
                            continue
                        else:
                            tiled_prod = True
                    refSubPath = refSubPaths[i]
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])

                    #loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band in list(refl_bands_dict.keys()):
                            if tiled_prod:
                                valBand = valSubPath + '\\' + band + name_sub_string + valSubPath.split('\\')[
                                    -1] + '.' + \
                                          file_ext
                                refBand = refSubPath + '\\' + band + name_sub_string + valSubPath.split('\\')[
                                    -1] + '.' + \
                                          file_ext
                            else:
                                valBand = valSubPath + '\\' + band + name_sub_string + test_metadata[
                                    'order_name'] + '.' + \
                                          file_ext
                                refBand = refSubPath + '\\' + band + name_sub_string + test_metadata[
                                    'order_name'] + '.' + \
                                          file_ext
                            valData = gdal.Open(valBand)
                            refData = gdal.Open(refBand)
                            valRaster = valData.GetRasterBand(1)
                            refRaster = refData.GetRasterBand(1)
                            valRasterAr = valRaster.ReadAsArray()
                            refRasterAr = refRaster.ReadAsArray()
                            lev2_1_tile_results, prod_test_sum = level_2_1_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_tile_results,
                                                                band)
                            test_sum += prod_test_sum
                    affected_bands = level_2_1_evaluation(lev2_1_tile_results, test_metadata['bands'])
                    tile_name = valSubPath.split('\\')[-1]
                    lev2_1_results[tile_name] = {
                        'affected_bands': affected_bands,
                        'level_2_1_details': lev2_1_tile_results
                    }

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
                    tiled_prod = False
                    if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                        if len(valSubPath.split('\\')[-1]) != 5:
                            continue
                        else:
                            tiled_prod = True
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])

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
                            lev2_1_tile_results = level_2_1_analysis(valRasterAr, refRasterAr, test_sum, lev2_1_tile_results,
                                                                band)
                    affected_bands, test_sum = level_2_1_evaluation(lev2_1_tile_results, test_metadata['bands'])
                    tile_name = valSubPath.split('\\')[-1]
                    lev2_1_results[tile_name] = {
                        'affected_bands': affected_bands,
                        'level_2_1_details': lev2_1_tile_results
                    }

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

def level_2_2_analysis(valRasterAr, refRasterAr, test_sum, lev2_2_tile_results, band, val_res_level_2_2_path,
                       test_metadata, tiled_prod, tile_name):
    print('Validating band ' + band)
    # check SR only no NoData values. Mask NoData
    valRasterAr = np.ma.masked_where(valRasterAr == 65535, valRasterAr).flatten()
    refRasterAr = np.ma.masked_where(refRasterAr == 65535, refRasterAr).flatten()
    difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float))
    # Todo: define thresholds and plots for differnces

    # calc difference statistics
    dif_band_sum = np.ma.sum(difRasterAr)
    test_sum += dif_band_sum

    if dif_band_sum != 0:
        print('Issues found in ' + band + '. Start calculating statistics.')
        dif_band_median = np.ma.median(difRasterAr)
        dif_band_mean = np.ma.mean(difRasterAr)
        dif_band_std = np.ma.std(difRasterAr)

        # calc reference dataset statistics
        ref_band_median = np.ma.median(refRasterAr)
        ref_band_mean = np.ma.mean(refRasterAr)
        ref_band_std = np.ma.std(refRasterAr)

        # calc validation dataset statistics
        val_band_median = np.ma.median(valRasterAr)
        val_band_mean = np.ma.mean(valRasterAr)
        val_band_std = np.ma.std(valRasterAr)

        #Todo: optimize plotting into bins
        # plot ref data histogram
        xlabel = 'Band ' + band
        ylabel = 'Frequency'
        title = test_metadata['order_name'] + '\n Reference data: Distribution of SR values of band ' + band
        if tiled_prod:
            plot_ref_file = val_res_level_2_2_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_ref_data_band_' + band + '_hist.png'
        else:
            plot_ref_file = val_res_level_2_2_path + '\\' + test_metadata[
                'order_name'] + '_ref_data_band_' + band + '_hist.png'
        plot_refl_histogram(refRasterAr, xlabel, ylabel, title, plot_ref_file)

        # plot ref data histogram
        xlabel = 'Band ' + band
        ylabel = 'Frequency'
        title = test_metadata['order_name'] + '\n Validation data: Distribution of SR values of band ' + band
        if tiled_prod:
            plot_val_file = val_res_level_2_2_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_val_data_band_' + band + '_hist.png'
        else:
            plot_val_file = val_res_level_2_2_path + '\\' + test_metadata[
                'order_name'] + '_val_data_band_' + band + '_hist.png'
        plot_refl_histogram(valRasterAr, xlabel, ylabel, title, plot_val_file)

        #Todo: make this plots nicer (title placement)
        # scatter plot
        xlabel = 'Reference dataset'
        ylabel = 'Validation dataset'
        title = test_metadata['order_name'] + '\n Scatterplot of reference against validation data band ' + band
        if tiled_prod:
            plot_scatter_file = val_res_level_2_2_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name +'_band_' + band + 'SR_scatter_plot.png'
        else:
            plot_scatter_file = val_res_level_2_2_path + '\\' + test_metadata[
            'order_name'] + '_band_' + band + 'SR_scatter_plot.png'
        ylim = (0, 20000)
        xlim = (0, 20000)
        refl_scatter_plot(refRasterAr, valRasterAr, xlabel, ylabel, title, plot_scatter_file, ylim, xlim)

        if dif_band_mean == dif_band_median and dif_band_std == .0:
            issue = 'Constant shift in SR'
        else:
            issue = 'Heterogeneous change in SR. Make further checks'

        lev2_2_tile_results[band] = {
            'test_level': 'L2.2',
            'passed': False,
            'summary': 'Statistics for band with differences',
            'issue': issue,
            'difference_statistics': {
                'median': str(dif_band_median),
                'mean': str(dif_band_mean),
                'std': str(dif_band_std)
            },
            'ref_dataset_statistics': {
                'median': str(ref_band_median),
                'mean': str(ref_band_mean),
                'std': str(ref_band_std)
            },
            'val_dataset_statistics': {
                'median': str(val_band_median),
                'mean': str(val_band_mean),
                'std': str(val_band_std)
            },
            'plots': {
                'ref_histogram': plot_ref_file,
                'val_histogram': plot_val_file,
                'scatter_plot': plot_scatter_file
            }
        }
    return lev2_2_tile_results, test_sum



def level_2_2(test_metadata, comparable, refl_bands_dict, name_sub_string, val_res_path):
    """
    Level 2 test no. 2: Distribution of SR values for both products
    """
    test_result = {
        'test_id': 'level_2_2',
        'test_name': 'Distribution of SR values for both products',
    }

    val_res_level_2_2_path = val_res_path + '\\lev_2_2_res'
    if not os.path.isdir(val_res_level_2_2_path):
        os.makedirs(val_res_level_2_2_path)

    if comparable:
        lev2_2_tile_results = {}
        lev2_2_results = {}
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
                    tiled_prod = False
                    if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                        if len(valSubPath.split('\\')[-1]) > 5:
                            continue
                        else:
                            tiled_prod = True
                    refSubPath = refSubPaths[i]
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])
                    tile_name = valSubPath.split('\\')[-1]

                    #loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band in list(refl_bands_dict.keys()):
                            if tiled_prod:
                                valBand = valSubPath + '\\' + band + name_sub_string + valSubPath.split('\\')[
                                    -1] + '.' + \
                                          file_ext
                                refBand = refSubPath + '\\' + band + name_sub_string + valSubPath.split('\\')[
                                    -1] + '.' + \
                                          file_ext
                            else:
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
                            lev2_2_tile_results, test_sum = level_2_2_analysis(valRasterAr, refRasterAr, test_sum,
                                                                               lev2_2_tile_results, band,
                                                                               val_res_level_2_2_path, test_metadata,
                                                                               tiled_prod, tile_name)
                    affected_bands = level_2_1_evaluation(lev2_2_tile_results, test_metadata['bands'])
                    tile_name = valSubPath.split('\\')[-1]
                    lev2_2_results[tile_name] = {
                        'affected_bands': affected_bands,
                        'level_2_2_details': lev2_2_tile_results
                    }

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
                    tiled_prod = False
                    if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                        if len(valSubPath.split('\\')[-1]) > 5:
                            continue
                        else:
                            tiled_prod = True
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])
                    tile_name = valSubPath.split('\\')[-1]

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
                            lev2_2_tile_results, test_sum = level_2_2_analysis(valRasterAr, refRasterAr, test_sum,
                                                                               lev2_2_tile_results, band,
                                                                               val_res_level_2_2_path, test_metadata,
                                                                               tiled_prod, tile_name)
                    affected_bands = level_2_1_evaluation(lev2_2_tile_results, test_metadata['bands'])
                    tile_name = valSubPath.split('\\')[-1]
                    lev2_2_results[tile_name] = {
                        'affected_bands': affected_bands,
                        'level_2_2_details': lev2_2_tile_results
                    }

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
            test_result['results'] = lev2_2_results

        except Exception as ex:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'error': ex,
            }
    else:
        print('L2.2 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

    return test_result


def level_2_3_analysis(valRasterAr, refRasterAr, test_sum, lev2_3_tile_results, aux_band_dict,
                       band, val_res_level_2_3_path, test_metadata, tiled_prod, tile_name):
    # check SR only no NoData values. Mask NoData
    valRasterAr = np.ma.masked_where(valRasterAr == 65535, valRasterAr).flatten()
    refRasterAr = np.ma.masked_where(refRasterAr == 65535, refRasterAr).flatten()
    difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float))
    # Todo: define thresholds and plots for differnces

    # calc difference statistics
    dif_band_sum = np.ma.sum(difRasterAr)
    test_sum += dif_band_sum

    if dif_band_sum != 0:
        dif_band_median = np.ma.median(difRasterAr)
        dif_band_mean = np.ma.mean(difRasterAr)
        dif_band_std = np.ma.std(difRasterAr)

        # calc reference dataset statistics
        ref_band_median = np.ma.median(refRasterAr)
        ref_band_mean = np.ma.mean(refRasterAr)
        ref_band_std = np.ma.std(refRasterAr)

        # calc validation dataset statistics
        val_band_median = np.ma.median(valRasterAr)
        val_band_mean = np.ma.mean(valRasterAr)
        val_band_std = np.ma.std(valRasterAr)

        #Todo: move plotting in seperate function
        #Todo: optimize plotting of classes
        # plot ref data histogram
        xlabel = 'Scene classification classes'
        ylabel = 'Frequency'
        title = test_metadata['order_name'] + '\n Reference data: Distribution of scene classification values'
        if tiled_prod:
            plot_ref_file = val_res_level_2_3_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_ref_data_scene_classification_hist.png'
        else:
            plot_ref_file = val_res_level_2_3_path + '\\' + test_metadata[
                'order_name'] + '_ref_data_scene_classification_hist.png'
        plot_histogram(refRasterAr, xlabel, ylabel, title, plot_ref_file)

        # plot ref data histogram
        xlabel = 'Scene classification classes'
        ylabel = 'Frequency'
        title = test_metadata['order_name'] + '\n Validation data: Distribution of scene classification values'
        if tiled_prod:
            plot_val_file = val_res_level_2_3_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_val_data_scene_classification_hist.png'
        else:
            plot_val_file = val_res_level_2_3_path + '\\' + test_metadata[
                'order_name'] + '_val_data_scene_classification_hist.png'
        plot_histogram(refRasterAr, xlabel, ylabel, title, plot_val_file)

        #Todo: make this plots nicer (title placement)
        # scatter plot
        xlabel = 'Reference dataset'
        ylabel = 'Validation dataset'
        title = test_metadata['order_name'] + '\n Scatterplot of reference against validation data'
        if tiled_prod:
            plot_scatter_file = val_res_level_2_3_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name +'_scene_classification_scatter_plot.png'
        else:
            plot_scatter_file = val_res_level_2_3_path + '\\' + test_metadata[
            'order_name'] + '_scene_classification_scatter_plot.png'
        ylim = (0, 12)
        xlim = (0, 12)
        scatter_plot(refRasterAr, valRasterAr, xlabel, ylabel, title, plot_scatter_file, ylim, xlim)

        if dif_band_mean == dif_band_median and dif_band_std == .0:
            issue = 'Constant shift in scene classification'
        else:
            issue = 'Heterogeneous change in scene classification. Make further checks'

        lev2_3_tile_results[aux_band_dict[band]] = {
            'test_level': 'L2.3',
            'passed': False,
            'summary': 'Statistics for scene classification',
            'issue': issue,
            'difference_statistics': {
                'median': str(dif_band_median),
                'mean': str(dif_band_mean),
                'std': str(dif_band_std)
            },
            'ref_dataset_statistics': {
                'median': str(ref_band_median),
                'mean': str(ref_band_mean),
                'std': str(ref_band_std)
            },
            'val_dataset_statistics': {
                'median': str(val_band_median),
                'mean': str(val_band_mean),
                'std': str(val_band_std)
            },
            'plots': {
                'ref_histogram': plot_ref_file,
                'val_histogram': plot_val_file,
                'scatter_plot': plot_scatter_file
            }
        }

    return lev2_3_tile_results, test_sum


def level_2_3(test_metadata, comparable, aux_band_dict, name_sub_string, val_res_path):
    """
    Level 2 test no. 3: Distribution of scene classification
    """

    val_res_level_2_3_path = val_res_path + '\\lev_2_3_res'
    if not os.path.isdir(val_res_level_2_3_path):
        os.makedirs(val_res_level_2_3_path)

    test_result = {
        'test_id': 'level_2_3',
        'test_name': 'Distribution of scene classification',
    }

    if comparable:
        lev2_3_tile_results = {}
        lev2_3_results = {}
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
                    tiled_prod = False
                    if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                        if len(valSubPath.split('\\')[-1]) > 5:
                            continue
                        else:
                            tiled_prod = True
                    refSubPath = refSubPaths[i]
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])
                    tile_name = valSubPath.split('\\')[-1]

                    #loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band == 'SCENE':
                            if tiled_prod:
                                valBand = valSubPath + '\\' + aux_band_dict[band] + name_sub_string + valSubPath.split('\\')[
                                    -1] + '.' + \
                                          file_ext
                                refBand = refSubPath + '\\' + aux_band_dict[band] + name_sub_string + valSubPath.split('\\')[
                                    -1] + '.' + \
                                          file_ext
                            else:
                                valBand = valSubPath + '\\' + aux_band_dict[band] + name_sub_string + test_metadata['order_name'] + '.' + \
                                          file_ext
                                refBand = refSubPath + '\\' + aux_band_dict[band] + name_sub_string + test_metadata['order_name'] + '.' + \
                                          file_ext
                            valData = gdal.Open(valBand)
                            refData = gdal.Open(refBand)
                            valRaster = valData.GetRasterBand(1)
                            refRaster = refData.GetRasterBand(1)
                            valRasterAr = valRaster.ReadAsArray()
                            refRasterAr = refRaster.ReadAsArray()
                            lev2_3_tile_results, test_sum = level_2_3_analysis(valRasterAr, refRasterAr, test_sum,
                                                                               lev2_3_tile_results,aux_band_dict, band,
                                                                               val_res_level_2_3_path, test_metadata,
                                                                               tiled_prod, tile_name)
                    affected_bands = level_2_1_evaluation(lev2_3_tile_results, test_metadata['bands'])
                    lev2_3_results[tile_name] = {
                        'affected_bands': affected_bands,
                        'level_2_3_details': lev2_3_tile_results
                    }

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
                    tiled_prod = False
                    tile_name = valSubPath.split('\\')[-1]
                    if valSubPath.split('\\')[-1] != test_metadata['order_name']:
                        if len(valSubPath.split('\\')[-1]) > 5:
                            continue
                        else:
                            tiled_prod = True
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])

                    refSubPath = refSubPaths[i]
                    valNetcdfFile = glob.glob(valSubPath + '\*.' + file_ext)[0]
                    refNetcdfFile = glob.glob(refSubPath + '\*.' + file_ext)[0]
                    valNetcdf = netCDF4.Dataset(valNetcdfFile, 'r')
                    refNetcdf = netCDF4.Dataset(refNetcdfFile, 'r')

                    # loop over refl bands listed in validation.json
                    for band in test_metadata['bands']:
                        if band in ['quality_scene_classification']:
                            valData = valNetcdf.variables[band][:,:]
                            refData = refNetcdf.variables[band][:,:]
                            valRasterAr = np.ma.filled(valData)
                            refRasterAr = np.ma.filled(refData)
                            tile_name = valSubPath.split('\\')[-1]
                            lev2_3_tile_results, test_sum = level_2_3_analysis(valRasterAr, refRasterAr, test_sum,
                                                                               lev2_3_tile_results,aux_band_dict, band,
                                                                               val_res_level_2_3_path, test_metadata,
                                                                               tiled_prod, tile_name)
                    affected_bands = level_2_1_evaluation(lev2_3_tile_results, test_metadata['bands'])
                    lev2_3_results[tile_name] = {
                        'affected_bands': affected_bands,
                        'level_2_3_details': lev2_3_tile_results
                    }

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
            test_result['results'] = lev2_3_results

        except Exception as ex:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'error': ex,
            }
    else:
        print('L2.3 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

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

        test_result['status'] = {
            'finished': True,
            'passed': test_passed
        }

    except Exception as ex:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': ex,
        }

    return test_result