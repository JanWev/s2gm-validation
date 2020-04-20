# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L2 tests. L2 checks for similarity of products
"""

import os
import glob
import json
import gdal
import netCDF4
import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'


def reclass_values(row):
    if row['count'] < 100:
        return 1
    elif row['count'] < 200:
        return 2
    elif row['count'] < 500:
        return 3
    elif row['count'] < 1000:
        return 4
    elif row['count'] < 2000:
        return 5
    elif row['count'] < 5000:
        return 6
    elif row['count'] < 10000:
        return 7
    elif row['count'] < 20000:
        return 8
    elif row['count'] < 50000:
        return 9
    elif row['count'] < 100000:
        return 10
    else:
        return 11


# def plot_histogram(refRasterAr, xlabel, ylabel, title, plot_file):
#     sns.set(color_codes=True)
#     sns.set(font_scale=1.5)
#     # sns.set_style("whitegrid")
#     plt.rcParams['figure.figsize'] = (8, 8)
#     fig, ax = plt.subplots(figsize=(10, 10))
#     ax.hist(refRasterAr)
#     ax.set(xlabel=xlabel,
#            ylabel=ylabel,
#            title=title)
#     plt.savefig(plot_file)
#     plt.clf()
#     plt.close()

def plot_histogram(plotRasterAr, xlabel, ylabel, title, plot_file, cut_zero):
    sns.set(color_codes=True)
    sns.set(font_scale=1.5)
    plt.rcParams['figure.figsize'] = (8, 8)
    fig, ax = plt.subplots(figsize=(10, 10))
    max_value = np.max(plotRasterAr) + 1
    if cut_zero:
        plotRasterAr = np.clip(plotRasterAr, 1, max_value)
    if max_value < 100:
        bins = list(range(0, max_value))
        f = ax.hist(plotRasterAr, bins=bins)
        ax.set(xlabel=xlabel,
               ylabel=ylabel,
               title=title)
        ax.xaxis.set_major_locator(plt.MultipleLocator(2))
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
        for i in range(max_value - 1):
            plt.text(f[1][i], f[0][i], str(f[0][i]))
        plt.tight_layout()
    else:
        ax.hist(plotRasterAr)
        ax.set(xlabel=xlabel,
               ylabel=ylabel,
               title=title)
    plt.savefig(plot_file)
    plt.clf()
    plt.close()


# def scatter_plot(refRasterAr, valRasterAr, xlabel, ylabel, title, plot_file, xlim, ylim):
# #     df = pd.DataFrame({'ref': refRasterAr, 'val': valRasterAr})
# #     h = sns.jointplot(x="val", y="ref", data=df, ylim=ylim, xlim=xlim)
# #     h.set_axis_labels(xlabel, ylabel, fontsize=12)
# #     h.fig.subplots_adjust(top=0.9)
# #     h.fig.suptitle(title, fontsize=12)
# #
# #     plt.savefig(plot_file)
# #     plt.clf()
# #     plt.close()

def scatter_plot(refRasterAr, valRasterAr, xlabel, ylabel, title, plot_file, group, subgroup, pointsize):
    df = pd.DataFrame({'ref': refRasterAr, 'val': valRasterAr})

    if group:
        xmax = round((df[['ref', 'val']].max(axis=1).max() * 1.6)).astype('int')
    else:
        xmax = df[['ref', 'val']].max(axis=1).max() * 1.1

    ymax = xmax
    xlim = (0, xmax)
    ylim = (0, ymax)

    if group:
        df_grouped = df.groupby(['ref', 'val']).size().reset_index().rename(columns={0: 'count'})
        if subgroup:
            df_grouped['groups'] = df_grouped.apply(lambda row: reclass_values(row), axis=1)
            h = plt.scatter(df_grouped['val'], df_grouped['ref'], c=df_grouped['groups'], s=pointsize, cmap="plasma",
                            alpha=0.7,
                            edgecolors='none')
        else:
            h = plt.scatter(df_grouped['val'], df_grouped['ref'], c=df_grouped['count'], s=pointsize, cmap="plasma",
                            alpha=0.7,
                            edgecolors='none')
        # h = sns.lmplot(x='val', y='ref', data=df_grouped, hue='count', fit_reg=False, scatter_kws={'s': 10}, legend=False).set(xlim=xlim, ylim=ylim)
        cbar = plt.colorbar(h, ticks=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        cbar.ax.set_yticklabels(
            ['< 100', '100-200', '200-500', '500-1K', '1K-2K', '2K-5K', '5K-10K', '10K-20K', '20K-50K', '50K-100K',
             '> 100K'])
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        # plt.legend(fontsize=4, ncol=3)
    else:
        # h = sns.jointplot(x='val', y='ref', data=df, ylim=ylim, xlim=xlim, joint_kws=dict(marker='o', s=10))
        h = sns.jointplot(x='val', y='ref', data=df, ylim=ylim, xlim=xlim)
        h.set_axis_labels(xlabel, ylabel, fontsize=12)
        h.fig.subplots_adjust(top=0.9)
        h.fig.suptitle(title, fontsize=12)

    plt.savefig(plot_file)
    plt.clf()
    plt.close()


def level_3_1_analysis_1(lev3_1_tile_results, valProdDifference,
                         refProdDifference):
    lev3_1_tile_results['metadata'] = {
        'test_level': 'L3.1',
        'passed': False,
        'summary': 'Difference in input products',
        'difference': 'Same number of input products, but names differ',
        'input_prod_not_in_val_data': str(valProdDifference),
        'input_prod_not_in_ref_data': str(refProdDifference)
    }
    return lev3_1_tile_results


def level_3_1_analysis_2(lev3_1_tile_results, refSourceProdList, valSourceProdList, valProdDifference,
                         refProdDifference):
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
        'input_prod_not_in_val_data': str(valProdDifference),
        'input_prod_not_in_ref_data': str(refProdDifference)
    }
    return lev3_1_tile_results


def level_3_1(test_metadata, ref_metadata, comparable, val_name_sub_string, ref_name_sub_string):
    """
    Level 3 test no. 1: Compare number of input products to mosaicking
    """
    test_result = {
        'test_id': 'level_3_1',
        'test_name': 'Compare number of input products to mosaicking',
    }

    if comparable:
        lev3_1_tile_results = {}
        lev3_1_results = {}
        try:
            if test_metadata['image_format'] == 'NETCDF':
                test_sum = 0
                file_ext = 'nc'
                valPath = test_metadata['validate_path']
                refPath = ref_metadata['reference_path']

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

                    refSubPath = refSubPaths[i]
                    valNetcdfFile = glob.glob(valSubPath + '\*.' + file_ext)[0]
                    refNetcdfFile = glob.glob(refSubPath + '\*.' + file_ext)[0]
                    valNetcdf = netCDF4.Dataset(valNetcdfFile, 'r')
                    refNetcdf = netCDF4.Dataset(refNetcdfFile, 'r')

                    valSourceProdString = valNetcdf.getncattr('input_components')
                    refSourceProdString = refNetcdf.getncattr('input_components')

                    valSourceProdList = re.split(',|=', valSourceProdString)[1::2]
                    refSourceProdList = re.split(',|=', refSourceProdString)[1::2]

                    valProdDifference = [x for x in valSourceProdList if x not in set(refSourceProdList)]
                    refProdDifference = [x for x in refSourceProdList if x not in set(valSourceProdList)]

                    if len(valSourceProdList) == len(refSourceProdList) and (
                            valProdDifference != [] or refProdDifference != []):
                        lev3_1_tile_results = level_3_1_analysis_1(lev3_1_tile_results, valProdDifference,
                                                                   refProdDifference)
                        tile_name = valSubPath.split('\\')[-1]
                        lev3_1_results[tile_name] = {
                            'level_3_1_details': lev3_1_tile_results
                        }
                        test_sum += 1
                    elif len(valSourceProdList) == len(refSourceProdList):
                        test_sum += 0
                    else:
                        lev3_1_tile_results = level_3_1_analysis_2(lev3_1_tile_results, refSourceProdList,
                                                                   valSourceProdList, valProdDifference,
                                                                   refProdDifference)
                        tile_name = valSubPath.split('\\')[-1]
                        lev3_1_results[tile_name] = {
                            'level_3_1_details': lev3_1_tile_results
                        }
                        test_sum += 1

            else:
                valPath = test_metadata['validate_path']
                refPath = ref_metadata['reference_path']

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
                        valFile = valSubPath + '\\' + 'metadata' + val_name_sub_string + valSubPath.split('\\')[
                            -1] + '.' + \
                                  'json'
                        refFile = refSubPath + '\\' + 'metadata' + ref_name_sub_string + refSubPath.split('\\')[
                            -1] + '.' + \
                                  'json'
                    else:
                        valFile = valSubPath + '\\' + 'metadata' + val_name_sub_string + test_metadata[
                            'order_name'] + '.' + \
                                  'json'
                        refFile = refSubPath + '\\' + 'metadata' + ref_name_sub_string + ref_metadata[
                            'order_name'] + '.' + \
                                  'json'

                    with open(str(valFile), 'r') as odf:
                        valJson = json.load(odf)
                    with open(str(refFile), 'r') as odf:
                        refJson = json.load(odf)

                    valSourceProdDict = valJson['Source_product_list']
                    refSourceProdDict = refJson['Source_product_list']

                    valSourceProdList = valSourceProdDict.values()
                    refSourceProdList = refSourceProdDict.values()

                    valProdDifference = [x for x in valSourceProdList if x not in set(refSourceProdList)]
                    refProdDifference = [x for x in refSourceProdList if x not in set(valSourceProdList)]

                    if len(valSourceProdList) == len(refSourceProdList) and (
                            valProdDifference != [] or refProdDifference != []):
                        lev3_1_tile_results = level_3_1_analysis_1(lev3_1_tile_results, valProdDifference,
                                                                   refProdDifference)
                        tile_name = valSubPath.split('\\')[-1]
                        lev3_1_results[tile_name] = {
                            'level_3_1_details': lev3_1_tile_results
                        }
                        test_sum += 1
                    elif len(valSourceProdDict) == len(refSourceProdDict):
                        test_sum += 0
                    else:
                        lev3_1_tile_results = level_3_1_analysis_2(lev3_1_tile_results, refSourceProdList,
                                                                   valSourceProdList, valProdDifference,
                                                                   refProdDifference)
                        tile_name = valSubPath.split('\\')[-1]
                        lev3_1_results[tile_name] = {
                            'level_3_1_details': lev3_1_tile_results
                        }
                        test_sum += 1

            if test_sum == 0:
                # fill test result
                test_passed = True
            else:
                test_passed = False

            test_result['status'] = {
                'finished': True,
                'passed': test_passed,
            }
            test_result['results'] = lev3_1_results

        except Exception as ex:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'error': str(ex),
            }
    else:
        print('L3.1 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

    return test_result


def level_3_2_evaluation(lev2_1_tile_results, bands):
    if len(lev2_1_tile_results) == len(bands):
        affected_bands = 'All'
    if len(lev2_1_tile_results) == 1:
        affected_bands = 'One'
    if len(lev2_1_tile_results) == 0:
        affected_bands = 'None'
    else:
        affected_bands = 'Some'

    return affected_bands


def level_3_2_analysis(valRasterAr, refRasterAr, valAuxRasterAr, refAuxRasterAr, test_sum, lev3_2_tile_results,
                       aux_band_dict, band, val_res_level_3_2_path, test_metadata, tiled_prod, tile_name):
    # check SR only no NoData values. Mask NoData
    valRasterArReclass = valRasterAr
    refRasterArReclass = refRasterAr
    valRasterAr = np.ma.masked_where(valRasterAr == 65535, valRasterAr).flatten()
    refRasterAr = np.ma.masked_where(refRasterAr == 65535, refRasterAr).flatten()
    difRasterAr = np.absolute(valRasterAr.astype(float) - refRasterAr.astype(float))

    # reclass medoid_mos
    valRasterArReclass[(valRasterArReclass > 0) & (valRasterArReclass < 65535)] = 1
    valRasterArReclass[(valRasterArReclass == 0) | (valRasterArReclass == 65535)] = 2
    valRasterArReclass[valAuxRasterAr == 65535] = 0
    valRasterArReclass = valRasterArReclass.flatten()

    refRasterArReclass[(refRasterArReclass > 0) & (refRasterArReclass < 65535)] = 1
    refRasterArReclass[(refRasterArReclass == 0) | (refRasterArReclass > 1)] = 2
    refRasterArReclass[refAuxRasterAr == 65535] = 0
    refRasterArReclass = refRasterArReclass.flatten()

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

        # Todo: move plotting in seperate function
        # Todo: optimize plotting of classes
        # plot ref data histogram
        xlabel = 'Algorithm Index'
        ylabel = 'Frequency'
        title = test_metadata['order_name'] + '\n Reference data: Distribution of algorithm used values'
        if tiled_prod:
            plot_ref_file = val_res_level_3_2_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_ref_data_algo_used_hist.png'
        else:
            plot_ref_file = val_res_level_3_2_path + '\\' + test_metadata[
                'order_name'] + '_ref_data_algo_used_hist.png'
        cut_zero = False
        plot_histogram(refRasterArReclass, xlabel, ylabel, title, plot_ref_file, cut_zero)

        # plot ref data histogram
        xlabel = 'Algorithm Index'
        ylabel = 'Frequency'
        title = test_metadata['order_name'] + '\n Validation data: Distribution of algorithm used values'
        if tiled_prod:
            plot_val_file = val_res_level_3_2_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_val_data_algo_used_hist.png'
        else:
            plot_val_file = val_res_level_3_2_path + '\\' + test_metadata[
                'order_name'] + '_val_data_algo_used_hist.png'
        cut_zero = False
        plot_histogram(valRasterArReclass, xlabel, ylabel, title, plot_val_file, cut_zero)

        # Todo: make this plots nicer (title placement)
        # scatter plot
        xlabel = 'Reference dataset'
        ylabel = 'Validation dataset'
        title = test_metadata['order_name'] + '\n Used algo scatterplot of reference against validation data'
        if tiled_prod:
            plot_scatter_file = val_res_level_3_2_path + '\\' + test_metadata[
                'order_name'] + '_' + tile_name + '_algo_used_scatter_plot.png'
        else:
            plot_scatter_file = val_res_level_3_2_path + '\\' + test_metadata[
                'order_name'] + '_algo_used_scatter_plot.png'

        grouped = True
        subgrouped = True
        pointsize = 20
        scatter_plot(refRasterArReclass, valRasterArReclass, xlabel, ylabel, title, plot_scatter_file, grouped,
                     subgrouped, pointsize)

        if dif_band_mean == dif_band_median and dif_band_std == .0:
            issue = 'Constant shift in algorithm used'
        else:
            issue = 'Heterogeneous change in used algorithm. Make further checks'

        lev3_2_tile_results[aux_band_dict[band]] = {
            'test_level': 'L3.2',
            'passed': False,
            'summary': 'Statistics for selected algorithm',
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

    return lev3_2_tile_results, test_sum


def level_3_2(test_metadata, ref_metadata, comparable, aux_band_dict, refl_bands_dict, val_name_sub_string,
              ref_name_sub_string, val_res_path):
    """
    Level 3 test no. 2: Compare applied algorithm
    """

    val_res_level_3_2_path = val_res_path + '\\lev_3_2_res'
    if not os.path.isdir(val_res_level_3_2_path):
        os.makedirs(val_res_level_3_2_path)

    test_result = {
        'test_id': 'level_3_2',
        'test_name': 'Distribution of scene classification',
    }

    if comparable:
        lev3_2_tile_results = {}
        lev3_2_results = {}
        all_band_dict = aux_band_dict.copy()
        all_band_dict.update(refl_bands_dict)
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
                refPath = ref_metadata['reference_path']

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
                    refSubPath = refSubPaths[i]
                    if tiled_prod:
                        print('Validating tile: ' + valSubPath.split('\\')[-1])
                    tile_name = valSubPath.split('\\')[-1]

                    # loop over refl bands listed in validation.json
                    if 'MEDOID_MOS' in test_metadata['bands'] and len(test_metadata['bands']) > 1:
                        band = 'MEDOID_MOS'
                        remain_band_list = test_metadata['bands'].copy()
                        remain_band_list.remove(band)
                        aux_band = str(remain_band_list[0])
                        if tiled_prod:
                            valBand = valSubPath + '\\' + all_band_dict[band] + val_name_sub_string + \
                                      valSubPath.split('\\')[-1] + '.' + file_ext
                            valAuxBand = valSubPath + '\\' + all_band_dict[aux_band] + val_name_sub_string + \
                                         valSubPath.split('\\')[-1] + '.' + file_ext
                            refBand = refSubPath + '\\' + all_band_dict[band] + ref_name_sub_string + \
                                      refSubPath.split('\\')[-1] + '.' + file_ext
                            refAuxBand = refSubPath + '\\' + all_band_dict[aux_band] + ref_name_sub_string + \
                                         refSubPath.split('\\')[-1] + '.' + file_ext
                        else:
                            valBand = valSubPath + '\\' + all_band_dict[band] + val_name_sub_string + \
                                      test_metadata['order_name'] + '.' + file_ext
                            valAuxBand = valSubPath + '\\' + all_band_dict[aux_band] + val_name_sub_string + \
                                         test_metadata['order_name'] + '.' + file_ext
                            refBand = refSubPath + '\\' + all_band_dict[band] + ref_name_sub_string + \
                                      ref_metadata['order_name'] + '.' + file_ext
                            refAuxBand = refSubPath + '\\' + all_band_dict[aux_band] + ref_name_sub_string + \
                                         ref_metadata['order_name'] + '.' + file_ext
                        valData = gdal.Open(valBand)
                        valAuxData = gdal.Open(valAuxBand)
                        refData = gdal.Open(refBand)
                        refAuxData = gdal.Open(refAuxBand)
                        valRaster = valData.GetRasterBand(1)
                        valAuxRaster = valAuxData.GetRasterBand(1)
                        refRaster = refData.GetRasterBand(1)
                        refAuxRaster = refAuxData.GetRasterBand(1)
                        valRasterAr = valRaster.ReadAsArray()
                        valAuxRasterAr = valAuxRaster.ReadAsArray()
                        refRasterAr = refRaster.ReadAsArray()
                        refAuxRasterAr = refAuxRaster.ReadAsArray()
                        lev3_2_tile_results, test_sum = level_3_2_analysis(valRasterAr, refRasterAr, valAuxRasterAr,
                                                                           refAuxRasterAr, test_sum,
                                                                           lev3_2_tile_results, aux_band_dict, band,
                                                                           val_res_level_3_2_path, test_metadata,
                                                                           tiled_prod, tile_name)
                        affected_bands = level_3_2_evaluation(lev3_2_tile_results, test_metadata['bands'])
                        lev3_2_results[tile_name] = {
                            'affected_bands': affected_bands,
                            'level_3_2_details': lev3_2_tile_results
                        }
                    else:
                        test_sum = 1
                        lev3_2_tile_results[aux_band_dict['MEDOID_MOS']] = {
                            'test_level': 'L3.2',
                            'passed': False,
                            'issue': 'Product has no MEDOID band'}
                        tile_name = valSubPath.split('\\')[-1]
                        lev3_2_results[tile_name] = {
                            'level_3_2_details': lev3_2_tile_results
                        }

            else:
                test_sum = 0
                valPath = test_metadata['validate_path']
                refPath = ref_metadata['reference_path']

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
                        print('Validating tile: ' + tile_name)

                    refSubPath = refSubPaths[i]
                    valNetcdfFile = glob.glob(valSubPath + '\*.' + file_ext)[0]
                    refNetcdfFile = glob.glob(refSubPath + '\*.' + file_ext)[0]
                    valNetcdf = netCDF4.Dataset(valNetcdfFile, 'r')
                    refNetcdf = netCDF4.Dataset(refNetcdfFile, 'r')

                    # loop over refl bands listed in validation.json
                    if 'MEDOID_MOS' in test_metadata['bands'] and len(test_metadata['bands']) > 1:
                        band = 'medoid_mos'
                        band_name = 'MEDOID_MOS'
                        remain_band_list = test_metadata['bands'].copy()
                        remain_band_list.remove('MEDOID_MOS')
                        aux_band = str(remain_band_list[0])
                        valData = valNetcdf.variables[band][:, :]
                        refData = refNetcdf.variables[band][:, :]
                        valAuxData = valNetcdf.variables[all_band_dict[aux_band]][:, :]
                        refAuxData = refNetcdf.variables[all_band_dict[aux_band]][:, :]
                        valRasterAr = np.ma.filled(valData)
                        refRasterAr = np.ma.filled(refData)
                        valAuxRasterAr = np.ma.filled(valAuxData)
                        refAuxRasterAr = np.ma.filled(refAuxData)

                        # flatten array
                        valRasterAr = valRasterAr.flatten()
                        refRasterAr = refRasterAr.flatten()
                        valAuxRasterAr = valAuxRasterAr.flatten()
                        refAuxRasterAr = refAuxRasterAr.flatten()

                        # unscale NetCDF
                        valRasterAr[valRasterAr != 65535] = valRasterAr[valRasterAr != 65535] * 10000
                        refRasterAr[refRasterAr != 65535] = refRasterAr[refRasterAr != 65535] * 10000
                        valAuxRasterAr[valAuxRasterAr != 65535] = valAuxRasterAr[valAuxRasterAr != 65535] * 10000
                        refAuxRasterAr[refAuxRasterAr != 65535] = refAuxRasterAr[refAuxRasterAr != 65535] * 10000

                        # convert to int
                        valRasterAr = valRasterAr.astype(np.uint)
                        refRasterAr = refRasterAr.astype(np.uint)
                        valAuxRasterAr = valAuxRasterAr.astype(np.uint)
                        refAuxRasterAr = refAuxRasterAr.astype(np.uint)

                        tile_name = valSubPath.split('\\')[-1]
                        lev3_2_tile_results, test_sum = level_3_2_analysis(valRasterAr, refRasterAr, valAuxRasterAr,
                                                                           refAuxRasterAr, test_sum,
                                                                           lev3_2_tile_results, aux_band_dict,
                                                                           band_name,
                                                                           val_res_level_3_2_path, test_metadata,
                                                                           tiled_prod, tile_name)
                        affected_bands = level_3_2_evaluation(lev3_2_tile_results, test_metadata['bands'])
                        lev3_2_results[tile_name] = {
                            'affected_bands': affected_bands,
                            'level_3_2_details': lev3_2_tile_results
                        }
                    else:
                        test_sum = 1
                        lev3_2_tile_results[aux_band_dict['MEDOID_MOS']] = {
                            'test_level': 'L3.2',
                            'passed': False,
                            'issue': 'Product has no MEDOID band'}
                        tile_name = valSubPath.split('\\')[-1]
                        lev3_2_results[tile_name] = {
                            'level_3_2_details': lev3_2_tile_results
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
            test_result['results'] = lev3_2_results

        except Exception as ex:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'error': str(ex),
            }
    else:
        print('L3.2 test could not be executed. Products have different request parameters and thus can not be '
              'compared')

    return test_result
