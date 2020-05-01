# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: create HTML report from ValidationOp validation result json
"""

import os
import argparse
import json
import numpy as np
import pandas as pd
# from weasyprint import HTML
from shutil import copyfile
from pathlib import Path

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

# enable long path names in table columns
pd.set_option('display.max_colwidth', -1)

def get_attributes(metadata):

    prod_name = metadata['order_name']

    return prod_name

def create_conc_html(val_order_data, order_list):
    html_conc_start = '''
    <h3>Conclusion: Check of test status</h3>
    '''
    html_conc_end = '''

    '''
    for idx1, prod_name in enumerate(order_list):
        for idx2, test in enumerate(val_order_data):
            prod_index = []
            test_index = []
            analysis_index = []
            status = []
            details_dict = val_order_data[test]['status']
            major = list(details_dict.keys())

            for major_key in major:
                if major_key != 'error':
                    prod_index.append(prod_name)
                    test_index.append(major_key)
                    analysis_index.append(test)
                    status.append(details_dict[major_key])

            index = [np.asanyarray(test_index), np.asanyarray(prod_index), np.asanyarray(analysis_index)]
            details_df_part = pd.DataFrame(np.asanyarray(status), index=index)
            details_df_part = details_df_part.unstack(level=0)
            if idx2 == 0:
                details_df = details_df_part
            else:
                details_df = pd.concat([details_df, details_df_part])
        if idx1 == 0:
            full_details_df = details_df
        else:
            full_details_df = pd.concat([full_details_df, details_df])
    results_html_table = full_details_df.to_html()

    html_conc_body = ''' 
    ''' + results_html_table + '''
    '''

    html_conc = html_conc_start + html_conc_body + html_conc_end

    return html_conc

def create_L0_1_html(val_order_data, order_list):
    html_L0_1_start = '''
    <h3>L0.1: Check of completeness</h3>
    '''
    html_L0_1_end = '''

    '''
    status = val_order_data['level_0_1']['status']
    if status['finished'] == False:
        print('Test L0.1 failed')
        html_L0_1_body = '''
        Test L0.1 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
        html_L0_1_body2 = ''''''

    else:
        html_L0_1_body = '''
        The test FINISHED
        '''
        if status['passed'] == True:
            html_L0_1_body2 = '''
            Test L0.1 FINISHED and PASSED: Integrity confirmed
            '''
        else:
            missing = val_order_data['level_0_1']['missing_files']
            missing_string = ' '.join(["<li>" + str(elem) + "</li>" for elem in missing])
            unexpected = val_order_data['level_0_1']['unexpected_files']
            unexpected_string = ' '.join(["<li>" + str(elem) + "</li>" for elem in unexpected])
            if missing != 0 and unexpected !=0:
                html_L0_1_body2 = '''
                Test L0.1 FINISHED but not PASSED: Difference found<br />
                Missing files: <ul>''' + missing_string + '''</ul>
                Unexpected files: <ul>''' + unexpected_string + '''</ul>
                '''
            elif missing != 0 and unexpected ==0:
                html_L0_1_body2 = '''
                Test L0.1 FINISHED but not PASSED: Difference found<br />
                Missing files: <ul>''' + missing_string + '''</ul>
                '''
            elif missing == 0 and unexpected !=0:
                html_L0_1_body2 = '''
                Test L0.1 FINISHED but not PASSED: Difference found<br />
                Unexpected files: <ul>''' + unexpected_string + '''</ul>
                '''

    html_L0_1 = html_L0_1_start + html_L0_1_body + html_L0_1_body2 + html_L0_1_end

    return html_L0_1

def create_L0_2_html(val_order_data, order_list):
    html_L0_2_start = '''
    <h3>L0.2: Check of integrity of files</h3>
    '''
    html_L0_2_end = '''

    '''
    status = val_order_data['level_0_2']['status']
    if status['finished'] == False:
        print('Test L0.2 failed')
        html_L0_2_body = '''
        Test L0.2 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
        html_L0_2_body2 = ''''''

    else:
        html_L0_2_body = '''
        The test was obviously SUCCESSFUL, but I have not worked on presenting results yet
        '''
        if status['passed'] == True:
            html_L0_2_body2 = '''
            Test L0.2 FINISHED and PASSED: Integrity confirmed
            '''
        else:
            html_L0_2_body2 = '''
            Test L0.2 FINISHED but not PASSED: Difference found<br />
            Error: ''' + val_order_data['level_0_2']['status']['Error'] + '''
            '''

    html_L0_2 = html_L0_2_start + html_L0_2_body + html_L0_2_body2 + html_L0_2_end

    return html_L0_2

def create_L1_0_html(product_folder, val_order_data, order_list, metadata):
    html_L1_0_start = '''
    <h3>L1.0: RGB quicklook and vrt stack</h3>
    '''
    html_L1_0_end = '''

    '''
    status = val_order_data['level_1_0']['status']
    if status['finished'] == False:
        print('Test failed')
        html_L1_0_body = '''
        Test FAILED<br />
        Error: ''' + status['error'] + '''
        '''
    else:
        # product_path = Path(metadata['validate_path'])
        product_path = Path("F:\\S2GM_ValidationTests\\NREFSD_LEI_TIFF\\S2GM_M10_20180811_20180831_S2GM_valreq_20200310T171427_stat01_T12LEI_STD_v1.0.4_43750")
        for subdir in product_path.iterdir():
            path = str(product_path / subdir)
            if subdir.is_dir():
                for file in os.listdir(path):
                    if file.endswith('tiff'):
                        tag = 'tif'
                    if file.endswith('jp2'):
                        tag = 'jp2'
                    if file.endswith('nc'):
                        tag = 'ns'

        body_parts_list = []
        for prod_name in order_list:
            if tag == 'tif' or tag == 'ns':
                html_L1_0_body_part = '''
                    Quicklook for ''' + prod_name + '''<br />
                    <img src="''' + product_folder + "\\val_res\\" + prod_name + ".png" + '''" style="width:500px;height:500px;"></img><br />
                    '''
                body_parts_list.append(html_L1_0_body_part)
            else:
                html_L1_0_body_part = '''
                    Quicklook for ''' + prod_name + '''<br />
                    <img src="''' + product_folder + "\\val_res\\" + prod_name + "_RGB.jpg" + '''" style="width:500px;height:500px;"></img><br />
                    '''
                body_parts_list.append(html_L1_0_body_part)

        html_L1_0_body = ''' '''.join([str(elem) for elem in body_parts_list])

    html_L1_0 = html_L1_0_start + html_L1_0_body + html_L1_0_end

    return html_L1_0


def create_L2_1_html(val_order_data, order_list):
    html_L2_1_start = '''
    <h3>L2.1: Spatial difference of SR for all bands</h3>
    '''
    html_L2_1_end = '''

    '''
    status = val_order_data['level_2_1']['status']
    if status['finished'] == False:
        print('Test L2.1 failed')
        html_L2_1_body = '''
        Test L2.1 FAILED<br />
        Error: ''' + status['error'] + '''
        
        '''
    else:
        body_parts_list = []
        for prod_name in order_list:
            affected_bands = val_order_data['level_2_1']['results'][prod_name]['affected_bands']

            band_index = []
            analysis_index = []
            data = []
            details_dict = val_order_data['level_2_1']['results'][prod_name]['level_2_1_details']
            major = list(details_dict.keys())
            minor = ['summary', 'difference']
            for major_key in major:
                for minor_key in minor:
                        band_index.append(major_key)
                        analysis_index.append(minor_key)
                        data.append(details_dict[major_key][minor_key])

            index = [np.asanyarray(analysis_index), np.asanyarray(band_index)]
            details_df = pd.DataFrame(np.asanyarray(data), index=index)
            details_df = details_df.unstack(level=0)
            results_html_table = details_df.to_html()
            html_L2_1_body_part = '''
            Results for: ''' + prod_name + '''<br /> 
            Number of affected bands: ''' + affected_bands + '''<br />''' + results_html_table + '''<br />
            '''
            body_parts_list.append(html_L2_1_body_part)

        html_L2_1_body_sumparts = ''' '''.join([str(elem) for elem in body_parts_list])

        if status['passed'] == True:
            html_L2_1_body = '''
                    Test L2.1 FINISHED and PASSED: Identical SR values<br />
                    ''' + html_L2_1_body_sumparts + '''
                    '''
        else:
            html_L2_1_body = '''
                    Test L2.1 FINISHED but not PASSED: Difference found<br />
                    ''' + html_L2_1_body_sumparts + '''
                    '''
    html_L2_1 = html_L2_1_start + html_L2_1_body + html_L2_1_end

    return html_L2_1


def create_L2_2_html(val_order_data, order_list):
    html_L2_2_start = '''
    <h3>L2.2: Distribution of SR values for both products</h3>
    '''
    html_L2_2_end = '''
    
    '''
    status = val_order_data['level_2_2']['status']
    if status['finished'] == False:
        print('Test L2.2 failed')
        html_L2_2_body = '''
        Test L2.2 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
    else:
        body_parts_list = []
        for prod_name in order_list:

            affected_bands = val_order_data['level_2_2']['results'][prod_name]['affected_bands']

            plot_band_index = []
            plot_analysis_index = []
            plot_index = []
            plot_data = []

            plot_details_dict = val_order_data["level_2_2"]["results"][prod_name]['level_2_2_details']
            plot_major = list(plot_details_dict.keys())
            plot_minor = ["plots"]
            plot_sub = ['scatter_plot', 'ref_histogram', 'val_histogram']
            for plot_major_key in plot_major:
                for plot_minor_key in plot_minor:
                    for plot_sub_key in plot_sub:
                        plot_band_index.append(plot_major_key)
                        plot_analysis_index.append(plot_minor_key)
                        plot_index.append(plot_sub_key)
                        plot_data.append('''<img src="''' + plot_details_dict[plot_major_key][plot_minor_key][plot_sub_key] + '''" style="width:300px;height:200px;"></img>''')

            plot_index = [np.asanyarray(plot_index), np.asanyarray(plot_analysis_index), np.asanyarray(plot_band_index)]
            plot_details_df = pd.DataFrame(np.asanyarray(plot_data), index=plot_index)

            plot_details_df = plot_details_df.unstack(level=0)
            plot_results_html_table = plot_details_df.to_html(escape=False)

            html_L2_2_plot_body_part = '''
                Results for: ''' + prod_name + '''<br />
                Number of affected bands: ''' + affected_bands + '''<br />
                Plots: ''' + plot_results_html_table + '''
                '''

            band_index = []
            analysis_index = []
            stat_index = []
            data = []
            details_dict = val_order_data['level_2_2']['results'][prod_name]['level_2_2_details']
            major = list(details_dict.keys())
            minor = ['difference_statistics', 'ref_dataset_statistics', 'val_dataset_statistics']
            sub = ['median', 'mean', 'std']
            for major_key in major:
                for minor_key in minor:
                    for sub_key in sub:
                        band_index.append(major_key)
                        analysis_index.append(minor_key)
                        stat_index.append(sub_key)
                        data.append(round(float(details_dict[major_key][minor_key][sub_key]), 4))

            index = [np.asanyarray(stat_index), np.asanyarray(analysis_index), np.asanyarray(band_index)]
            details_df = pd.DataFrame(np.asanyarray(data), index=index)
            details_df = details_df.unstack(level=0)
            results_html_table = details_df.to_html()

            html_L2_2_body_part = '''
                Numbers: ''' + results_html_table + '''<br />
                '''
            body_parts_list.append(html_L2_2_plot_body_part + html_L2_2_body_part)


        html_L2_2_body_sumparts = ''' '''.join([str(elem) for elem in body_parts_list])

        if status['passed'] == True:
            html_L2_2_body = '''
                    Test L2.2 FINISHED and PASSED: Identical SR values<br />
                    ''' + html_L2_2_body_sumparts + '''
                    '''
        else:
            html_L2_2_body = '''
                    Test L2.2 FINISHED but not PASSED: Difference found<br />
                    ''' + html_L2_2_body_sumparts + '''
                    '''
    html_L2_2 = html_L2_2_start + html_L2_2_body + html_L2_2_end

    return html_L2_2


def create_L2_3_html(val_order_data, order_list):
    html_L2_3_start = '''
    <h3>L2.3: Distribution of scene classification</h3>
    '''
    html_L2_3_end = '''

    '''
    status = val_order_data['level_2_3']['status']
    if status['finished'] == False:
        print('Test L2.3 failed')
        html_L2_3_body = '''
        Test L2.3 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
    else:
        body_parts_list = []
        for prod_name in order_list:
            affected_bands = val_order_data['level_2_3']['results'][prod_name]['affected_bands']

            plot_band_index = []
            plot_analysis_index = []
            plot_index = []
            plot_data = []

            plot_details_dict = val_order_data["level_2_3"]["results"][prod_name]['level_2_3_details']
            plot_major = list(plot_details_dict.keys())
            plot_minor = ["plots"]
            plot_sub = ['scatter_plot', 'ref_histogram', 'val_histogram']
            for plot_major_key in plot_major:
                for plot_minor_key in plot_minor:
                    for plot_sub_key in plot_sub:
                        plot_band_index.append(plot_major_key)
                        plot_analysis_index.append(plot_minor_key)
                        plot_index.append(plot_sub_key)
                        plot_data.append('''<img src="''' + plot_details_dict[plot_major_key][plot_minor_key][
                            plot_sub_key] + '''" style="width:300px;height:200px;"></img>''')

            plot_index = [np.asanyarray(plot_index), np.asanyarray(plot_analysis_index), np.asanyarray(plot_band_index)]
            plot_details_df = pd.DataFrame(np.asanyarray(plot_data), index=plot_index)

            plot_details_df = plot_details_df.unstack(level=0)
            plot_results_html_table = plot_details_df.to_html(escape=False)

            html_L2_3_plot_body_part = '''
                Results for: ''' + prod_name + '''<br />
                Number of affected bands: ''' + affected_bands + '''<br />
                Plots: ''' + plot_results_html_table + '''
                '''

            band_index = []
            analysis_index = []
            stat_index = []
            data = []
            details_dict = val_order_data['level_2_3']['results'][prod_name]['level_2_3_details']
            major = list(details_dict.keys())
            minor = ['difference_statistics', 'ref_dataset_statistics', 'val_dataset_statistics']
            sub = ['median', 'mean', 'std']
            for major_key in major:
                for minor_key in minor:
                    for sub_key in sub:
                        band_index.append(major_key)
                        analysis_index.append(minor_key)
                        stat_index.append(sub_key)
                        data.append(round(float(details_dict[major_key][minor_key][sub_key]), 4))

            index = [np.asanyarray(stat_index), np.asanyarray(analysis_index), np.asanyarray(band_index)]
            details_df = pd.DataFrame(np.asanyarray(data), index=index)
            details_df = details_df.unstack(level=0)
            results_html_table = details_df.to_html()

            html_L2_3_body_part = '''
                    Numbers: ''' + results_html_table + '''<br />
                    '''
            body_parts_list.append(html_L2_3_plot_body_part + html_L2_3_body_part)

        html_L2_3_body_sumparts = ''' '''.join([str(elem) for elem in body_parts_list])

        if status['passed'] == True:
            html_L2_3_body = '''
                    Test L2.3 FINISHED and PASSED: Identical SR values<br />
                    ''' + html_L2_3_body_sumparts + '''
                    '''
        else:
            html_L2_3_body = '''
                    Test L2.3 FINISHED but not PASSED: Difference found<br />
                    ''' + html_L2_3_body_sumparts + '''
                    '''
    html_L2_3 = html_L2_3_start + html_L2_3_body + html_L2_3_end

    return html_L2_3

def create_L2_4_html(val_order_data, order_list):
    html_L2_4_start = '''
    <h3>L2.4: Distribution of source_index</h3>
    '''
    html_L2_4_end = '''

    '''
    status = val_order_data['level_2_4']['status']
    if status['finished'] == False:
        print('Test L2.4 failed')
        html_L2_4_body = '''
        Test L2.4 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
    else:
        body_parts_list = []
        for prod_name in order_list:
            affected_bands = val_order_data['level_2_4']['results'][prod_name]['affected_bands']

            plot_band_index = []
            plot_analysis_index = []
            plot_index = []
            plot_data = []

            plot_details_dict = val_order_data["level_2_4"]["results"][prod_name]['level_2_4_details']
            plot_major = list(plot_details_dict.keys())
            plot_minor = ["plots"]
            plot_sub = ['scatter_plot', 'ref_histogram', 'val_histogram']
            for plot_major_key in plot_major:
                for plot_minor_key in plot_minor:
                    for plot_sub_key in plot_sub:
                        plot_band_index.append(plot_major_key)
                        plot_analysis_index.append(plot_minor_key)
                        plot_index.append(plot_sub_key)
                        plot_data.append('''<img src="''' + plot_details_dict[plot_major_key][plot_minor_key][
                            plot_sub_key] + '''" style="width:300px;height:200px;"></img>''')

            plot_index = [np.asanyarray(plot_index), np.asanyarray(plot_analysis_index), np.asanyarray(plot_band_index)]
            plot_details_df = pd.DataFrame(np.asanyarray(plot_data), index=plot_index)

            plot_details_df = plot_details_df.unstack(level=0)
            plot_results_html_table = plot_details_df.to_html(escape=False)

            html_L2_4_plot_body_part = '''
                Results for: ''' + prod_name + '''<br />
                Number of affected bands: ''' + affected_bands + '''<br />
                Plots: ''' + plot_results_html_table + '''
                '''

            band_index = []
            analysis_index = []
            stat_index = []
            data = []
            details_dict = val_order_data['level_2_4']['results'][prod_name]['level_2_4_details']
            major = list(details_dict.keys())
            minor = ['difference_statistics', 'ref_dataset_statistics', 'val_dataset_statistics']
            sub = ['median', 'mean', 'std']
            for major_key in major:
                for minor_key in minor:
                    for sub_key in sub:
                        band_index.append(major_key)
                        analysis_index.append(minor_key)
                        stat_index.append(sub_key)
                        data.append(round(float(details_dict[major_key][minor_key][sub_key]), 4))

            index = [np.asanyarray(stat_index), np.asanyarray(analysis_index), np.asanyarray(band_index)]
            details_df = pd.DataFrame(np.asanyarray(data), index=index)
            details_df = details_df.unstack(level=0)
            results_html_table = details_df.to_html()

            html_L2_4_body_part = '''
                        Numbers: ''' + results_html_table + '''<br />
                        '''
            body_parts_list.append(html_L2_4_plot_body_part + html_L2_4_body_part)

        html_L2_4_body_sumparts = ''' '''.join([str(elem) for elem in body_parts_list])

        if status['passed'] == True:
            html_L2_4_body = '''
                    Test L2.4 FINISHED and PASSED: Identical SR values<br />
                    ''' + html_L2_4_body_sumparts + '''
                    '''
        else:
            html_L2_4_body = '''
                    Test L2.4 FINISHED but not PASSED: Difference found<br />
                    ''' + html_L2_4_body_sumparts + '''
                    '''
    html_L2_4 = html_L2_4_start + html_L2_4_body + html_L2_4_end

    return html_L2_4

def create_L3_1_html(val_order_data, order_list):
    html_L3_1_start = '''
    <h3>L3.1: Compare number of input products to mosaicking</h3>
    '''
    html_L3_1_end = '''

    '''
    status = val_order_data['level_3_1']['status']
    if status['finished'] == False:
        print('Test L3.1 failed')
        html_L3_1_body = '''
        Test L3.1 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
    else:
        if status['passed'] == True:
            html_L3_1_body = '''
                    Test L3.1 FINISHED and PASSED: Identical values
                    '''
        else:
            body_parts_list = []
            for prod_name in order_list:
                analysis_index = []
                data = []
                details_dict_metadata = val_order_data['level_3_1']['results'][prod_name]['level_3_1_details']['metadata']
                minor = ['summary', 'difference', 'count_ref_prod', 'count_val_prod', 'input_prod_not_in_val_data', 'input_prod_not_in_ref_data']
                for minor_key in minor:
                    if minor_key in details_dict_metadata:
                        analysis_index.append(minor_key)
                        data.append(details_dict_metadata[minor_key])

                index = [np.asanyarray(analysis_index)]
                details_df = pd.DataFrame(np.asanyarray(data), index=index)
                results_html_table = details_df.to_html()

                html_L3_1_body_part = '''
                    Results for: ''' + prod_name + '''<br /> 
                    ''' + results_html_table + '''<br />
                    '''
                body_parts_list.append(html_L3_1_body_part)

            html_L3_1_body_sumparts = ''' '''.join([str(elem) for elem in body_parts_list])

            html_L3_1_body = '''
                    Test L3.1 FINISHED but not PASSED: Difference found
                    ''' + html_L3_1_body_sumparts + '''
                    '''
    html_L3_1 = html_L3_1_start + html_L3_1_body + html_L3_1_end

    return html_L3_1

def create_L3_2_html(val_order_data, order_list):
    html_L3_2_start = '''
    <h3>L3.2: Distribution of scene classification</h3>
    '''
    html_L3_2_end = '''

    '''
    status = val_order_data['level_3_2']['status']
    if status['finished'] == False:
        print('Test L3.2 failed')
        html_L3_2_body = '''
        Test L3.2 FAILED<br />
        Error: ''' + status['error'] + '''
        '''
    else:
        if status['passed'] == True:
            html_L3_2_body = '''
                    Test L3.2 FINISHED and PASSED: Identical SR values<br />
                    '''
        else:
            body_parts_list = []
            for prod_name in order_list:
                try:
                    affected_bands = val_order_data['level_3_2']['results'][prod_name]['affected_bands']
                    issue = val_order_data["level_3_2"]["results"][prod_name]['level_3_2_details']['medoid_mos']['issue']

                    plot_analysis_index = []
                    plot_index = []
                    plot_data = []

                    plot_details_dict = val_order_data["level_3_2"]["results"][prod_name]['level_3_2_details']['medoid_mos']
                    plot_minor = ["plots"]
                    plot_sub = ['scatter_plot', 'ref_histogram', 'val_histogram']
                    for plot_minor_key in plot_minor:
                        for plot_sub_key in plot_sub:
                            plot_analysis_index.append(plot_minor_key)
                            plot_index.append(plot_sub_key)
                            plot_data.append('''<img src="''' + plot_details_dict[plot_minor_key][
                                plot_sub_key] + '''" style="width:300px;height:200px;"></img>''')

                    plot_index = [np.asanyarray(plot_analysis_index), np.asanyarray(plot_index)]
                    plot_details_df = pd.DataFrame(np.asanyarray(plot_data), index=plot_index)

                    plot_details_df = plot_details_df.unstack(level=0)
                    plot_results_html_table = plot_details_df.to_html(escape=False)

                    html_L3_2_plot_body_part = '''
                        Results for: ''' + prod_name + '''<br />
                        Number of affected bands: ''' + affected_bands + '''<br />
                        Issue: ''' + issue + '''<br />
                        Plots: ''' + plot_results_html_table + '''
                        '''

                    analysis_index = []
                    stat_index = []
                    data = []
                    details_dict = val_order_data['level_3_2']['results'][prod_name]['level_3_2_details']['medoid_mos']
                    minor = ['difference_statistics', 'ref_dataset_statistics', 'val_dataset_statistics']
                    sub = ['median', 'mean', 'std']
                    for minor_key in minor:
                        for sub_key in sub:
                            analysis_index.append(minor_key)
                            stat_index.append(sub_key)
                            data.append(round(float(details_dict[minor_key][sub_key]), 4))

                    index = [np.asanyarray(analysis_index), np.asanyarray(stat_index)]
                    details_df = pd.DataFrame(np.asanyarray(data), index=index)
                    details_df = details_df.unstack(level=0)
                    results_html_table = details_df.to_html()

                    html_L3_2_body_part = '''
                                    Numbers: ''' + results_html_table + '''<br />
                                    '''
                    body_parts_list.append(html_L3_2_plot_body_part + html_L3_2_body_part)
                except:
                    issue = val_order_data["level_3_2"]["results"][prod_name]['level_3_2_details']['medoid_mos']['issue']

                    html_L3_2_plot_body_part = '''
                                            Results for: ''' + prod_name + '''<br />
                                            Issue: ''' + issue + '''<br />
                                            '''
                    body_parts_list.append(html_L3_2_plot_body_part)

            html_L3_2_body_sumparts = ''' '''.join([str(elem) for elem in body_parts_list])

            html_L3_2_body = '''
                    Test L3.2 FINISHED but not PASSED: Difference or error found<br />
                    ''' + html_L3_2_body_sumparts + '''
                    '''
    html_L3_2 = html_L3_2_start + html_L3_2_body + html_L3_2_end

    return html_L3_2



def create_html(vr_folder, metadata):
    vrf = vr_folder + '/validation_report.json'
    lev_2_2_res = vr_folder + '/lev_2_2_res'
    lev_2_3_res = vr_folder + '/lev_2_3_res'
    lev_2_4_res = vr_folder + '/lev_2_4_res'
    lev_3_2_res = vr_folder + '/lev_3_2_res'

    with open(str(vrf), 'r') as vr:
        val_order_data = json.load(vr)

    all_prod_name = get_attributes(metadata)
    product_folder = os.path.dirname(vr_folder)
    subdirpathlist = [f.path for f in os.scandir(product_folder) if f.is_dir()]
    order_list = []
    for p in subdirpathlist:
        a = p.split('\\')[-1]
        if a != 'val_res':
            order_list.append(a)

    html_start = '''
    <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=utf-8" />
            <link rel="stylesheet" type="text/css" href="reset.css" media="screen" />
            <link rel="stylesheet" type="text/css" href="style.css" media="screen" />
        </head>
        <body>
            <div id="container">
              <div id="header">
                <h1>Validation Report:</h1>
                <h2>''' + all_prod_name + '''</h2>
              </div>
              <!--//end #headern//-->
              <div id="centerColumn">

    '''
    html_Lconc_start = '''
                <!-- *** Test Conclusion *** --->
                <h2>Overview</h2>

                '''

    html_Lconc_1 = create_conc_html(val_order_data, order_list)

    html_Lconc_end = '''

        '''
    html_Lconc = html_Lconc_start + html_Lconc_1 + html_Lconc_end

    html_L0_start = '''
            <!-- *** L0 Tests *** --->
            <h2>Level 0: Product integrity</h2>

            '''

    html_L0_1 = create_L0_1_html(val_order_data, order_list)

    html_L0_2 = create_L0_2_html(val_order_data, order_list)

    html_L0_end = '''

    '''

    html_L0 = html_L0_start + html_L0_1 + html_L0_2 + html_L0_end

    html_L1_start = '''
            <!-- *** L1 Tests *** --->
            <h2>Level 1: Product plausibility</h2>

            '''
    html_L1_0 = create_L1_0_html(product_folder, val_order_data, order_list, metadata)

    html_L1_end = '''

    '''
    html_L1 = html_L1_start + html_L1_0 + html_L1_end


    html_L2_start = '''
            <!-- *** L2 Tests *** --->
            <h2>Level 2: Product verification</h2>
            '''
    html_L2_1 = create_L2_1_html(val_order_data, order_list)

    html_L2_2 = create_L2_2_html(val_order_data, order_list)

    html_L2_3 = create_L2_3_html(val_order_data, order_list)

    html_L2_4 = create_L2_4_html(val_order_data, order_list)

    html_L2_end = '''

    '''
    html_L2 = html_L2_start + html_L2_1 + html_L2_2 + html_L2_3 + html_L2_4 + html_L2_end


    html_L3_start = '''
            <!-- *** L3 Tests *** --->
            <h2>Level 3: Product validation</h2>
            '''
    html_L3_1 = create_L3_1_html(val_order_data, order_list)

    html_L3_2 = create_L3_2_html(val_order_data, order_list)

    html_L3_end = '''

    '''
    html_L3 = html_L3_start + html_L3_1 + html_L3_2 + html_L3_end


    html_end = '''
                <blockquote>
              <p><strong>blockquote</strong><br />
                Augur et fulgente decorus arcu Phoebus acceptusque novem Camenis, qui salutari levat arte fessos corporis artus.</p>
            </blockquote>
          </div>
          <!--//end #centerColumn//-->
          <div id="footer"> <a target="_blank" href="http://validator.w3.org/" title="W3C HTML Validation">XHTML</a> | <a target="_blank" href="http://jigsaw.w3.org/css-validator/validator-uri.html" title="W3C CSS Validation">CSS</a> | <a target="_blank" href="http://www.w3.org/TR/WCAG10/" title="Web Content Accessibility Guidelines">WCAG</a> | <a target="_blank" rel="nofollow" href="http://www.csstinderbox.com">The CSS Tinderbox</a>
            </p>
          </div>
          <!--//end #footer//-->
        </div>
        <!--//end #container//-->
        </body>
        </html>
        
        '''

    html_string = html_start + html_Lconc + html_L0 + html_L1 + html_L2 + html_L3 + html_end


    f = open(vr_folder + '/report.html', 'w')
    f.write(html_string)
    f.close()
    # HTML(string=html_string).write_pdf(vr_folder + '/report.pdf')

    #copyfile('./aux_data/style.css', vr_folder + '/style.css')
    #copyfile('./aux_data/reset.css', vr_folder + '/reset.css')

    scriptDirectory = os.path.dirname(os.path.dirname(__file__))
    #scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    copyfile(scriptDirectory + '\\aux_data\\style.css', vr_folder + '/style.css')
    copyfile(scriptDirectory + '\\aux_data\\reset.css', vr_folder + '/reset.css')


if __name__ == "__main__":
    CLI = argparse.ArgumentParser(
        description="This script turns a json validation report and additional other results to a html report")
    CLI.add_argument(
        "-r",
        "--results",
        type=str,
        required=False,
        metavar="path",
        help='Path and validation results folder'
    )
    args = CLI.parse_args()
    create_html(args.results + '/val_res')
