# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: create HTML report from ValidationOp validation result json
"""

import os
import argparse
import json
import numpy as np
import pandas as pd
from weasyprint import HTML
from shutil import copyfile

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

url = 'https://land.copernicus.eu/imagery-in-situ/global-image-mosaics/sites/default/files/Southern_France2_60m_annual2017_subset2_small2.png'

def get_attributes(val_order_data):
    prod_name = val_order_data['base_info']['product_name']

    return prod_name

def create_L2_2_html(val_order_data, prod_name):
    html_L2_2_start = '''
    <h3>L2.2: Distribution of SR values for both products</h3>
    '''
    html_L2_2_end = '''
    
    '''
    status = val_order_data['level_2_2']['status']
    if status['finished'] == False:
        print('Test failed')
        html_L2_2_body = '''
        Test FAILED
        '''
    else:
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

        index = [np.asanyarray(band_index), np.asanyarray(analysis_index), np.asanyarray(stat_index)]
        details_df = pd.DataFrame(np.asanyarray(data), index=index)
        details_df = details_df.unstack(level=0)
        results_html_table = details_df.to_html()

        if status['passed'] == True:
            html_L2_2_body = '''
                    Test FINISHED: Identical SR values
                    ''' + results_html_table + '''
                    '''
        else:
            html_L2_2_body = '''
                                Test FINISHED: Difference found
                                ''' + results_html_table + '''
                    '''
    html_L2_2 = html_L2_2_start + html_L2_2_body + html_L2_2_end

    return html_L2_2


def create_html(vr_folder):
    vrf = vr_folder + '/validation_report.json'
    lev_2_2_res = vr_folder + '/lev_2_2_res'
    lev_2_3_res = vr_folder + '/lev_2_3_res'
    lev_2_4_res = vr_folder + '/lev_2_4_res'
    lev_3_2_res = vr_folder + '/lev_3_2_res'

    with open(str(vrf), 'r') as vr:
        val_order_data = json.load(vr)

    prod_name = get_attributes(val_order_data)
    create_L2_2_html(val_order_data, prod_name)

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
                <h2>''' + val_order_data['base_info']['product_name'] + '''</h2>
              </div>
              <!--//end #headern//-->
              <div id="leftColumn">
                <h2>leftColumn</h2>
                <ul>
                  <li><a href="#">Link Item</a></li>
                  <li><a href="#">Link Item</a></li>
                  <li><a href="#">Link Item</a></li>
                </ul>
                <p>Augur et fulgente decorus arcu Phoebus acceptusque novem Camenis, qui salutari 
                  levat arte fessos corporis artus.</p>
              </div>
              <!--//end #leftColumn//-->
              <div id="centerColumn">

    '''

    html_L0 = '''
            <!-- *** L0 Tests *** --->
            <h2>Level 0: Product integrity</h2>
            <h3>L0.1: Check of completeness</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            <h3>L0.2: Check of integrity of files</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            
            '''
    html_L1 = '''
            <!-- *** L1 Tests *** --->
            <h2>Level 1: Product plausibility</h2>
            <h3>NO L1 TESTS IMPLEMENTED<h3>
            
            '''

    html_L2_start = '''
            <!-- *** L2 Tests *** --->
            <h2>Level 2: Product verification</h2>
            '''
    html_L2_1 = '''
            <h3>L2.1: SR difference for all available bands</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            '''
    html_L2_2 = create_L2_2_html(val_order_data, prod_name)

    html_L2_3 = '''
            <h3>L2.3: Distribution of scene classification</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            '''
    html_L2_4 = '''
            <h3>L2.4: Distribution of source_index</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            '''
    html_L2_end = '''
    
    '''
    html_L2 = html_L2_start + html_L2_1 + html_L2_2 + html_L2_3 + html_L2_4 + html_L2_end

    html_L3 = '''
            <!-- *** L3 Tests *** --->
            <h2>Level 3: Product verification</h2>
            <h3>L3.1: Compare number of input products to mosaicking</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            <h3>L3.2: Compare applied algorithm</h3>
            <iframe frameborder="0" seamless="seamless" scrolling="no" 
            src="''' + url + '''"></iframe>
            <p>Figure title</p>
            
            '''
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

    html_string = html_start + html_L0 + html_L1 + html_L2 + html_L3 + html_end


    f = open(vr_folder + '/report.html', 'w')
    f.write(html_string)
    f.close()
    HTML(string=html_string).write_pdf(vr_folder + '/report.pdf')

    copyfile('../aux_data/style.css', vr_folder + '/style.css')
    copyfile('../aux_data/reset.css', vr_folder + '/reset.css')

    # scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    # copyfile(scriptDirectory + '/aux_data/style.css', vr_folder + '/style.css')
    # copyfile(scriptDirectory + '/aux_data/reset.css', vr_folder + '/reset.css')


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
