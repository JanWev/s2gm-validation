# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate request and download of s2gm products.

example commands:
1. python ValidationOp.py --operators 1 --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --TOKEN eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MjBhYjE5ZS0xMjFhLTQ3ZWMtYWQ3ZS0yOTMwNmE0YzIyMzkiLCJhdWQiOiJjNTI1NDQ0Yy02YmQ0LTQyOTAtYjU2Zi0xMWI3OTI0OTE0NjUiLCJqdGkiOiI5OWJkNWNkMzA3NjM0YjQ0MmU2ZmQ3MmM2ZGUzYWU3YyIsImV4cCI6MTUzNDkzMDgxOSwibmFtZSI6IkphbiBXZXZlcnMiLCJlbWFpbCI6Imphbi53ZXZlcnNAYnJvY2ttYW5uLWNvbnN1bHQuZGUiLCJnaXZlbl9uYW1lIjoiSmFuIiwiZmFtaWx5X25hbWUiOiJXZXZlcnMiLCJhY2NvdW50Ijp7InR5cGUiOjEwMDB9fQ.KKuFf3_PbHmMRsT8ATZ5y23jQchAnt9yKKlxo3HcSYFqlVi3f6LqJOTtynnMJr0W_F3_LCJMLDdMLC0mHYrX2varjE5lbKiyctcHjdZ2p_1ytJ3yykvN5BwndvrkDFyAewM-AVX_qT279-hmhn89IEHrjEURX7tf7XVtWc_-Hc7JsbH2HnjL0raOEpl_L-7F2lxNda7DbuaTkx4kFRmiHtDgWo3EsH-hy299apmcMDhsrNHy4flSKap5hGn1G3ZTEGbQaor6-bnOrIjganZfquO9pKxtlZxyNa0tk0Esy5ldArv6Hx8EpGI_NJWIH4IHZp12cNtfI7_KSoT8HxfBmw
2. first time use (incl randomization): python ValidationOp.py -r --operators 1  --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --TOKEN eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MjBhYjE5ZS0xMjFhLTQ3ZWMtYWQ3ZS0yOTMwNmE0YzIyMzkiLCJhdWQiOiJjNTI1NDQ0Yy02YmQ0LTQyOTAtYjU2Zi0xMWI3OTI0OTE0NjUiLCJqdGkiOiI5OWJkNWNkMzA3NjM0YjQ0MmU2ZmQ3MmM2ZGUzYWU3YyIsImV4cCI6MTUzNDkzMDgxOSwibmFtZSI6IkphbiBXZXZlcnMiLCJlbWFpbCI6Imphbi53ZXZlcnNAYnJvY2ttYW5uLWNvbnN1bHQuZGUiLCJnaXZlbl9uYW1lIjoiSmFuIiwiZmFtaWx5X25hbWUiOiJXZXZlcnMiLCJhY2NvdW50Ijp7InR5cGUiOjEwMDB9fQ.KKuFf3_PbHmMRsT8ATZ5y23jQchAnt9yKKlxo3HcSYFqlVi3f6LqJOTtynnMJr0W_F3_LCJMLDdMLC0mHYrX2varjE5lbKiyctcHjdZ2p_1ytJ3yykvN5BwndvrkDFyAewM-AVX_qT279-hmhn89IEHrjEURX7tf7XVtWc_-Hc7JsbH2HnjL0raOEpl_L-7F2lxNda7DbuaTkx4kFRmiHtDgWo3EsH-hy299apmcMDhsrNHy4flSKap5hGn1G3ZTEGbQaor6-bnOrIjganZfquO9pKxtlZxyNa0tk0Esy5ldArv6Hx8EpGI_NJWIH4IHZp12cNtfI7_KSoT8HxfBmw

!IMPORTANT!
Set the DOWNLOAD_FOLDER variable in static_parameters.py to a local folder on your computer!

PARAMETERS:
-r: set -r flag to randomize parameters: Don't randomize parameters(default)

--operators: 0=create only parameters, 1(default)=request only, 2=status check only, 3=download only, 4=request, status and download

--test: can be kept empty

--USERID: your uder ID from MosaicHub. description see below or ask Jan Wevers
The user id also needs to be acquired from the mosic hub web site.
Again, login with your credentials and open the developer tools in your
browser. Make sure to navigate to "Network" inside the developer tools and
select the "Response" section. Browse to "UserArea" inside The mosaic hub.
In the developer tools window you will find two entries named 'orders'.
If you select the second one, you will get a long string. Inside the string
you will find an entry called "userId": Copy the string and use as parameter.

--DOWNLOAD_FOLDER: indicate download folder like K:/S2GM/S2GM_mosaics/v0.6.5/Python_downloads/

--TOKEN
The bearer token has to be updated every time you run this tool and the last
execution was more than two hours ago.
The bearer token has to be aquired from the mosaic hub web site.
Login with your credentials. Activate the developer tools of your browser.
Make sure to navigate to "Network" inside the developer tools and select
the "Headers" section. Browse to "UserArea" inside The mosaic hub.
In the developer tools window you will find two entries named 'orders'.
In the second you will find under "Request Headers" an entry called
"Authorization: Bearer". The complete string afterwards has to be copied
below under token. The token will be active for 2 hours.
"""

import os
import json
import argparse
import logging
from datetime import datetime, date
from validation_tools.utilities import parameter_definition, product_requester, order_status_checker, product_downloader
from validation_tools.utilities.static_parameters import DOWNLOAD_FOLDER

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'


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
        resolution = '"R' + request_parameters[2][str(counter)] + 'm"'
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


def main(RANDOMIZE, operators, USERID, DOWNLOAD_FOLDER, TOKEN):
    try:
        logging.basicConfig(filename='./logs/execution.log', filemode='a',level=logging.DEBUG)
        logging.info('RequestDownloadOp executed: %s', str(datetime.now()))
        logging.debug('Operator executed by the user: %s', str(operators))
    except FileNotFoundError:
        print('log file does not exist and will be created')
        f = open('./logs/execution.log')
        f.close()
        logging.basicConfig(filename='./logs/execution.log', filemode='a', level=logging.DEBUG)
        logging.info('RequestDownloadOp executed: %s', str(datetime.now()))
        logging.debug('Operator executed by the user: %s', str(operators))

    if operators == 0:
        request_parameters, num_products = parameter_definition.get_parameters(DOWNLOAD_FOLDER, RANDOMIZE)
    else:
        request_parameters, num_products = parameter_definition.get_parameters(DOWNLOAD_FOLDER, RANDOMIZE)
        if operators == 1: # request only
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = product_requester.run(DOWNLOAD_FOLDER, TOKEN, data, prod_id)
                if status_code == 404:
                    print(json.loads(data)['name'] + ' not available')
                else:
                    print(json.loads(data)['name'] + ' ordered')
        if operators == 2: # status check only
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = order_status_checker.run(DOWNLOAD_FOLDER, TOKEN, prod_id)
                if status_code == 401:
                    continue
                elif status_code == None:
                    continue
                else:
                    print(json.loads(data)['name'] + ' ready for download')
        if operators == 3: # download only
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = product_downloader.run(TOKEN, DOWNLOAD_FOLDER, prod_id)
                if status_code == 900:
                    pass
                elif status_code == 404:
                    pass
                else:
                    print('Download complete: ' + json.loads(data)['name'])
        if operators == 4: # request, status check and download
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = product_requester.run(DOWNLOAD_FOLDER, TOKEN, data, prod_id)
                if status_code == 404:
                    print(json.loads(data)['name'] + ' not available')
                else:
                    print(json.loads(data)['name'] + ' ordered')
            for prod_id in range(1, num_products + 1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = order_status_checker.run(DOWNLOAD_FOLDER, TOKEN, prod_id)
                if status_code == 401:
                    continue
                elif status_code == None:
                    continue
                else:
                    print(json.loads(data)['name'] + ' ready for download')
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = product_downloader.run(TOKEN, DOWNLOAD_FOLDER, prod_id)
                if status_code == 900:
                    pass
                elif status_code == 404:
                    pass
                else:
                    print('Download complete: ' + json.loads(data)['name'])


if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "-r",
        action="store_true",
        default=False,
        help = "set -r flag to randomize parameters: Don't randomize parameters(default)"
    )
    CLI.add_argument(
        "--operators",
        nargs="*",
        type=int,
        default=1,
        help='0=create only parameters, 1=request only, 2=status check only, 3=download only, 4=request, status and download'
    )
    CLI.add_argument(
        "--USERID",
        nargs="*",
        type=str,
        default='',
        help='user ID needed'
    )
    CLI.add_argument(
        "--TOKEN",
        nargs="*",
        type=str,
        default='',
        help='insert bearer token from MosaicHub'
    )
    # parse the command line
    args = CLI.parse_args()
    main(args.r, args.operators[0], args.USERID, DOWNLOAD_FOLDER, args.TOKEN[0])