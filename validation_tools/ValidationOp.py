# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import sys
import argparse
import logging
from datetime import datetime
#from utilities import parameter_definition, product_downloader
from validation_tools.utilities import parameter_definition, product_downloader

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

# The bearer token has to be updated every time you run this tool and the last
# execution was more than two hours ago.
# The bearer token has to be aquired from the mosaic hub web site.
# Login with your credentials. Activate the developer tools of your browser.
# Make sure to navigate to "Network" inside the developer tools and select
# the "Headers" section. Browse to "UserArea" inside The mosaic hub.
# In the developer tools window you will find two entries named 'orders'.
# In the second you will find under "Request Headers" an entry called
# "Authorization: Bearer". The complete string afterwards has to be copied
# below under token. The token will be active for 2 hours.
# TOKEN = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MjBhYjE5ZS0xMjFhLTQ3ZWMtYWQ3ZS0yOTMwNmE0YzIyMzkiLCJhdWQiOiJjNTI1NDQ0Yy02YmQ0LTQyOTAtYjU2Zi0xMWI3OTI0OTE0NjUiLCJqdGkiOiJhMTZjMGFkMmIyMTEzNWI5NTg3MmI5ODBkNTAzY2FlNyIsImV4cCI6MTUzNDI2MjUxNywibmFtZSI6IkphbiBXZXZlcnMiLCJlbWFpbCI6Imphbi53ZXZlcnNAYnJvY2ttYW5uLWNvbnN1bHQuZGUiLCJnaXZlbl9uYW1lIjoiSmFuIiwiZmFtaWx5X25hbWUiOiJXZXZlcnMiLCJhY2NvdW50Ijp7InR5cGUiOjEwMDB9fQ.DuN8FCH6-UgCK69lTbLroNOcbIi3wjU6W_hi7WejgsTqcOzpkPxVN_zT7wuD-jTZfEKcTuAQ5Jo0Juiww5JNqQFkExsddclsA1_P2nwXctGGXvnvpLViKRIxQzZKzvQcJA6ihXYsb1EUVERzLz_Ruu-zG2OwNVG1462Wd2AwtWHZieA7mvyiRh5grSgC4ppbESVd1IB9rjOFKJybg6nWYRexabEEzINbpAnDTZWR1M5rglDaPlkR7WUOAYO2RV4Kdx6_N2QklaRtayGub58OYzWm7XDDa930JRWCccQHYq4yD_RzkYpW4yIV2_Isn5u4Y1VTJKXYCSycjyxvkinkCg'
TOKEN = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MjBhYjE5ZS0xMjFhLTQ3ZWMtYWQ3ZS0yOTMwNmE0YzIyMzkiLCJhdWQiOiJjNTI1NDQ0Yy02YmQ0LTQyOTAtYjU2Zi0xMWI3OTI0OTE0NjUiLCJqdGkiOiI2MzhhOTgyMTA5YzAyNzIzYzYyZGI4YmNkMWUzYjg4OCIsImV4cCI6MTUzNDc4NDMzNiwibmFtZSI6IkphbiBXZXZlcnMiLCJlbWFpbCI6Imphbi53ZXZlcnNAYnJvY2ttYW5uLWNvbnN1bHQuZGUiLCJnaXZlbl9uYW1lIjoiSmFuIiwiZmFtaWx5X25hbWUiOiJXZXZlcnMiLCJhY2NvdW50Ijp7InR5cGUiOjEwMDB9fQ.iBAnBmyjaoP6oSK9ph8wZNHcWwfyLdrFOY-vIKD94hS9_33Svr-_5zCOzY2pzcN_xcYdivdZtuBvMUDSyo-b64KQt5X1lH53PZkPNrzxf4POA1PSAdEubZlQRBA1mHgDa2wZKIu-I7TYhZ0ptOQuS6msqAhGXFAvcwIR53qhWQJbSiqvLA20zMtkxA1zSVoPVfvWwMQvXV2SJl_WS_092oLe2QcIoVSj9J5_CWLVYunYUTbdRNmX5IGkgEkp0XiXsDhie1UgikEDtMOOGLrte35hn4n747Yq76Ky3mA7Ygd2neraS7OUsUCAx3Oj5492Y6LhctyDAUMQpa9K_eAAHA'
USERID = '820ab19e-121a-47ec-ad7e-29306a4c2239'
DOWNLOAD_FOLDER = 'K:/S2GM/S2GM_mosaics/v0.6.5/Python_downloads/' #Set for your System

def log_inputs(tests):
    logging.basicConfig(filename='execution.log', filemode='a',level=logging.DEBUG)
    logging.info('ValidationOp executed: %s', str(datetime.now()))
    logging.debug('Requested tests by the user: %s', str(tests))

def parameter_writer(counter, request_parameters, userid):
    if counter < 10:
        name = '"' + request_parameters[0]['0'+str(counter)] + '"'
        imageFormat = '"' + request_parameters[1]['0' + str(counter)] + '"'
        resolution = '"R' + request_parameters[2]['0' + str(counter)] + 'm"'
        coordsys = '"' + request_parameters[3]['0' + str(counter)] + '"'
        bands = request_parameters[4]['0' + str(counter)]
        coordinates = (request_parameters[5]['0' + str(counter)])
        period = '"' + (request_parameters[6]['0' + str(counter)]) + '"'
        date = (request_parameters[7]['0' + str(counter)])

        data = '{"name":' + name + ',' + '"status":"ORDER_PLACED","created":' + \
               '""' + ',"imageFormat":' + imageFormat + \
               ',"resolution":' + resolution + ',"coordinateSystem":' + \
               coordsys + ',"additionalData":' + bands + ',"userId":"' + \
               userid + '","areaOfInterest":{"crs":{"type":"name",' \
                        '"properties":{"name":"urn:ogc:def:crs:EPSG::4326"}},' \
                        '"type":"MultiPolygon",' \
                        '"coordinates":[[[' + coordinates + ']]]},"startDate":"' \
               + date +'Z",' \
                       '"temporalPeriod":'+ period + '}'
    else:
        name = '"' + request_parameters[0][str(counter)] + '"'
        imageFormat = '"' + request_parameters[1][str(counter)] + '"'
        resolution = 'R' + request_parameters[2][str(counter)] + 'm'
        coordsys = '"' + request_parameters[3][str(counter)] + '"'
        bands = request_parameters[4][str(counter)]
        coordinates = (request_parameters[5][str(counter)])
        period = '"' + (request_parameters[6][str(counter)]) + '"'
        date = (request_parameters[7][str(counter)])

        data = '{"name":' + name + ',' + '"status":"ORDER_PLACED","created":' + \
               '""' + ',"imageFormat":' + imageFormat + \
               ',"resolution":' + resolution + ',"coordinateSystem":' + \
               coordsys + ',"additionalData":' + bands + ',"userId":"' + \
               userid + '","areaOfInterest":{"crs":{"type":"name",' \
                        '"properties":{"name":"urn:ogc:def:crs:EPSG::4326"}},' \
                        '"type":"MultiPolygon",' \
                        '"coordinates":[[[' + coordinates + ']]]},"startDate":"' \
               + date +'Z",' \
                       '"temporalPeriod":'+ period + '}'
    return data


def main(tests, USERID):
    log_inputs(tests)
    request_parameters, num_products = parameter_definition.get_parameters()
    for i in range(1,num_products+1):
        print(i)
    i = 1
    data = parameter_writer(i, request_parameters, USERID[0])
    print(data)
    product_downloader.control(TOKEN, USERID, DOWNLOAD_FOLDER, data)


    # Tests to be executed here:
    ## L0
    ## L1
    ## L2


if __name__ == "__main__":
    #input_one = sys.argv[1]
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--tests",# name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=int,
        default=[1, 2, 3], # default if nothing is provided
        help='index numbers of wanted tests. usage: --tests 1 2 5 6. default --tests 1 2 3'
    )
    CLI.add_argument(
        "--USERID",# name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str,
        default='', # default if nothing is provided
        help='user ID needed'
    )
    # parse the command line
    args = CLI.parse_args()
    main(args.tests, args.USERID)