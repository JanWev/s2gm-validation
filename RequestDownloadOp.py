# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate request and download of s2gm products.

example commands:
1. create parameters: RequestDownloadOp.py --operators 0 --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --FOLDER 0116_1124
2. make request: RequestDownloadOp.py --operators 1 --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --FOLDER 0116_1124
3. check processing status: RequestDownloadOp.py --operators 2 --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --FOLDER 0116_1124
4. download products: RequestDownloadOp.py --operators 3 --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --FOLDER 0116_1124
5. convert pickel to json request information: RequestDownloadOp.py --operators 4 --USERID 820ab19e-121a-47ec-ad7e-29306a4c2239 --FOLDER 0116_1124

!IMPORTANT!
A few variables need to be set in the static_parameters.py. This script needs to be activated by removing ".dist".
Set the username, password variable in static_parameters.py to access the Mosaic Hub.
Also set DOWNLOAD_FOLDER variable in static_parameters.py to a local folder on your computer!

PARAMETERS:
-r: set -r flag to randomize parameters: Don't randomize parameters(default)

--operators: 0=create only parameters, 1(default)=request only, 2=status check only, 3=download only, 4=convert pickel to json

--USERID: your user ID from MosaicHub. description see below or ask Jan Wevers
The user id also needs to be acquired from the mosic hub web site.
Again, login with your credentials and open the developer tools in your
browser. Make sure to navigate to "Network" inside the developer tools and
select the "Response" section. Browse to "UserArea" inside The mosaic hub.
In the developer tools window you will find two entries named 'orders'.
If you select the second one, you will get a long string. Inside the string
you will find an entry called "userId": Copy the string and use as parameter.

--FOLDER: subfolder to store your products in. It is recommended to use a date_time construction like 0116_1129

ADDITIONAL HELP:
By using the -r flag, the randomizable parameters get randomized again. It is recommended to to this only if an
existing randomization should be repeated or randomization failed and thus needs to be redone. In general the -r flag
is not specifically needed.

When running the RequestDownloaderOp it is recommended to to it in the steps shown in the examples above.
1.  Run the script with --operators 0 to create parameters. Randomizable parameters will be randomized by default. If
    you need to run  it again, for example because you have deleted log files, simply run it again and the randomizer
    will not be triggered. If randomization is needed use the -r flag.
2.  Execute the script with --operators 1 to make a request at the S2GM Hub.
3.  Execute the script with --operator 2 to check the processing status. This can be repeated until all products have
    reached the status processing finished.
4.  Run the script with --operator 3 to download the data
5.  Execute the script with --operator 4 to create validation.json file in each product folder holding the request
    information for validation.
"""

import os
import json
import argparse
import logging
import pickle
from datetime import datetime
from validation_tools.utilities import parameter_definition, product_requester, order_status_checker, \
    product_downloader, pickel_to_json_converter
from validation_tools.utilities.static_parameters import username, password, DOWNLOAD_FOLDER, version_number
from validation_tools.utilities.get_token import get_token

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
    if len(DOWNLOAD_FOLDER) > 48:
        exit('Download path too long. Please shorten path! Maximum allowed path length for DOWNLOAD_FOLDER: 48 chracters')
    else:
        pass
    if not os.path.isdir('./logs'):
        os.makedirs('./logs')
    if not os.path.isdir(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    if operators == 0:
        try:
            logging.basicConfig(filename=DOWNLOAD_FOLDER + 'parameter.log', filemode='a', level=logging.DEBUG)
            logging.info('Parameters for the following products have been created: %s', str(datetime.now()))
        except FileNotFoundError:
            print('log file does not exist and will be created')
            f = open(DOWNLOAD_FOLDER + 'parameter.log')
            f.close()
            logging.basicConfig(filename=DOWNLOAD_FOLDER + 'parameter.log', filemode='a', level=logging.DEBUG)
            logging.info('Parameters for the following products have been created: %s', str(datetime.now()))
        request_parameters, num_products = parameter_definition.get_parameters(DOWNLOAD_FOLDER, RANDOMIZE)
        with open(DOWNLOAD_FOLDER + 'variables/request_parameters.pkl', 'wb') as f:
            pickle.dump(request_parameters, f)
        print(request_parameters)
        for i in range(1, num_products+1):
            if i < 10:
                logging.info('name: %s', request_parameters[0]['0' + str(i)])
                logging.info('format: %s', request_parameters[1]['0' + str(i)])
                logging.info('resolution: %s', request_parameters[2]['0' + str(i)])
                logging.info('projection: %s', request_parameters[3]['0' + str(i)])
                logging.info('bands: %s', request_parameters[4]['0' + str(i)])
                logging.info('coordinates: %s', request_parameters[5]['0' + str(i)])
                logging.info('period: %s', request_parameters[6]['0' + str(i)])
                logging.info('date: %s \n', request_parameters[7]['0' + str(i)])
            else:
                logging.info('name: %s', request_parameters[0][str(i)])
                logging.info('format: %s', request_parameters[1][str(i)])
                logging.info('resolution: %s', request_parameters[2][str(i)])
                logging.info('projection: %s', request_parameters[3][str(i)])
                logging.info('bands: %s', request_parameters[4][str(i)])
                logging.info('coordinates: %s', request_parameters[5][str(i)])
                logging.info('period: %s', request_parameters[6][str(i)])
                logging.info('date: %s \n', request_parameters[7][str(i)])
    else:
        request_parameters, num_products = parameter_definition.get_parameters(DOWNLOAD_FOLDER, RANDOMIZE)
        with open(DOWNLOAD_FOLDER + 'variables/request_parameters.pkl', 'wb') as f:
            pickle.dump(request_parameters, f)
        if operators == 1: # request only
            try:
                logging.basicConfig(filename=DOWNLOAD_FOLDER + 'request.log', filemode='a', level=logging.DEBUG)
                logging.info('The following products have been requested on: %s', str(datetime.now()))
                logging.info('Product name and status:')
            except FileNotFoundError:
                print('log file does not exist and will be created')
                f = open(DOWNLOAD_FOLDER + 'request.log')
                f.close()
                logging.basicConfig(filename=DOWNLOAD_FOLDER + 'request.log', filemode='a', level=logging.DEBUG)
                logging.info('The following products have been requested on: %s', str(datetime.now()))
                logging.info('Product name and status:')
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code = product_requester.run(DOWNLOAD_FOLDER, TOKEN, data, prod_id)
                if status_code != 200:
                    print(json.loads(data)['name'] + ' not available')
                    logging.info(json.loads(data)['name'] + ' not available')
                else:
                    print(json.loads(data)['name'] + ' ordered')
                    logging.info(json.loads(data)['name'] + ' ordered')

        elif operators == 2: # status check only
            try:
                logging.basicConfig(filename=DOWNLOAD_FOLDER + 'status.log', filemode='a', level=logging.DEBUG)
                logging.info('Processing status of files: %s', str(datetime.now()))
                logging.info('Product name and status:')
            except FileNotFoundError:
                print('log file does not exist and will be created')
                f = open(DOWNLOAD_FOLDER + 'status.log')
                f.close()
                logging.basicConfig(filename=DOWNLOAD_FOLDER + 'status.log', filemode='a', level=logging.DEBUG)
                logging.info('Processing status of files: %s', str(datetime.now()))
                logging.info('Product name and status:')
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                status_code, status = order_status_checker.run(DOWNLOAD_FOLDER, TOKEN, prod_id)
                if status_code == 401:
                    print('status code' + str(status_code))
                    continue
                elif status_code == None:
                    print('status code' + str(status_code))
                    continue
                else:
                    if status == 'FINISHED':
                        print(json.loads(data)['name'] + ' ready for download')
                        logging.info(json.loads(data)['name'] + ' ready for download')
                    elif status == 'PARTIALLY_FINISHED':
                        print(json.loads(data)['name'] + ' partially ready for download')
                        logging.info(json.loads(data)['name'] + ' partially ready for download')
                    elif status == 'UNAVAILABLE':
                        print(json.loads(data)['name'] + ' product rejected during request')
                        logging.info(json.loads(data)['name'] + ' product rejected during request')
                    elif status == 'FAILURE':
                        print(json.loads(data)['name'] + ' something went wrong - not sure what happend')
                        logging.info(json.loads(data)['name'] + ' something went wrong - not sure what happend')
                    else:
                        print(json.loads(data)['name'] + ' still processing')
                        logging.info(json.loads(data)['name'] + ' still processing')

        elif operators == 3: # download only
            try:
                logging.basicConfig(filename=DOWNLOAD_FOLDER + 'download.log', filemode='a', level=logging.DEBUG)
                logging.info('Download status of files: %s', str(datetime.now()))
                logging.info('Product name and status:')
            except FileNotFoundError:
                print('log file does not exist and will be created')
                f = open(DOWNLOAD_FOLDER + 'download.log')
                f.close()
                logging.basicConfig(filename=DOWNLOAD_FOLDER + 'download.log', filemode='a', level=logging.DEBUG)
                logging.info('Download status of files: %s', str(datetime.now()))
                logging.info('Product name and status:')
            for prod_id in range(1,num_products+1):
                data = parameter_writer(prod_id, request_parameters, USERID[0])
                # Todo: find a clever way to to make this variable. Now the upper limit is set to 10000 products in order list
                for list_number in range(0, 11000, 100):
                    # print(list_number)
                    status_code = product_downloader.run(TOKEN, DOWNLOAD_FOLDER, prod_id, list_number, version_number)
                    if status_code == 900:
                        pass
                    elif status_code == 404:
                        pass
                    else:
                        print('Download complete: ' + json.loads(data)['name'])
                        logging.info('Download complete: ' + json.loads(data)['name'])
        elif operators == 4:  # convert pickl to json
            for prod_id in range(1, num_products + 1):
                pickel_to_json_converter.run(DOWNLOAD_FOLDER, prod_id)
        else:
            print('The operator number ' + str(operators) + ' you have chosen is not defined')



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
        "--FOLDER",
        nargs="*",
        type=str,
        default='',
        help='insert subfolder name for products e.g. with date and time like 0116_1115'
    )

    TOKEN = get_token(username, password)
    # parse the command line
    args = CLI.parse_args()
    DOWNLOAD_FOLDER = DOWNLOAD_FOLDER + args.FOLDER[0] + '/'
    main(args.r, args.operators[0], args.USERID, DOWNLOAD_FOLDER, TOKEN)