# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import os
import requests
import logging
from datetime import datetime, timedelta
import time
import shutil
import calendar
import pickle

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
#TOKEN = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MjBhYjE5ZS0xMjFhLTQ3ZWMtYWQ3ZS0yOTMwNmE0YzIyMzkiLCJhdWQiOiJjNTI1NDQ0Yy02YmQ0LTQyOTAtYjU2Zi0xMWI3OTI0OTE0NjUiLCJqdGkiOiI2NWE3MGQwZTU0NTM3Y2Q3MzhkZjUwOGU0OGE3ZjkzNSIsImV4cCI6MTUzNDc1OTQxNywibmFtZSI6IkphbiBXZXZlcnMiLCJlbWFpbCI6Imphbi53ZXZlcnNAYnJvY2ttYW5uLWNvbnN1bHQuZGUiLCJnaXZlbl9uYW1lIjoiSmFuIiwiZmFtaWx5X25hbWUiOiJXZXZlcnMiLCJhY2NvdW50Ijp7InR5cGUiOjEwMDB9fQ.uByL1xDQ4vc0HLq-GnfSmH7DbNthO3-tONZzZHX0LxJ837OnDuO7ATut8FViqHF2XJZg-byG5iAGAgkeuC2lwmXo97r4vbOmmOuvdAl3VMoq-h4BLQxGkllfgAiqm1maGlYm2WtPcr0MHcRuJ1JpEN6G_i9_kwhFoaEuACbpNLS0aCDpaf9HhVK-LiVKbEbJnNeVhDSvxnnTxaIYiw2CWehWxFZyUrjMg7KRJ8ixBI-DIyQSdB-x9KjBP3f-IoS9Z3OEsL2kZUIl855BkuD3lTcEFczOpczT9KQuWOtuY4lqkYdLSuqPrBDPlp6ToIlwULMj9S5AesojEukKA2a4vw'
# The user id also needs to be acquired from the mosic hub web site.
# Again, login with your credentials and open the developer tools in your
# browser. Make sure to navigate to "Network" inside the developer tools and
# select the "Response" section. Browse to "UserArea" inside The mosaic hub.
# In the developer tools window you will find two entries named 'orders'.
# If you select the second one, you will get a long string. Inside the string
# you will find an entry called "userId":
# Copy the string afterwards to USERID below.
#USERID = '820ab19e-121a-47ec-ad7e-29306a4c2239'
#DOWNLOAD_FOLDER = 'K:/S2GM/S2GM_mosaics/v0.6.5/Python_downloads/' #Set for your System

def log_request(html_status):
    logging.basicConfig(filename='./logs/execution.log', filemode='a',
                        level=logging.DEBUG)
    logging.info('Request data at mosaic hub  : %s', str(datetime.now()))
    logging.debug('HTML status: %s', str(html_status))


def log_processing(request_id, done, count):
    logging.basicConfig(filename='./logs/execution.log', filemode='a',
                        level=logging.DEBUG)
    if count == 0:
        logging.info('Processing has started  : %s', str(datetime.now()))
    if done:
        logging.info('Processing of request %s in S2GM hub is finished: %s',
                     request_id, str(datetime.now()))
        logging.info('Ready for download %s', str(datetime.now()))
    else:
        logging.debug('Processing of request %s not finished yet: %s',
                      request_id, str(datetime.now()))


def log_download(start, running, finished, url):
    logging.basicConfig(filename='./logs/execution.log', filemode='a',
                        level=logging.DEBUG)
    print('Start value: %s \n', str(start))
    print('Stop value: %s \n', str(finished))
    if start and not finished:
        logging.info('Download started  : %s', str(datetime.now()))
        # logging.debug('Requested tests by the user: %s', str(''))

    if start and not finished and running:
        logging.debug('Downloading %s: %s', url, str(datetime.now()))

    if start and finished:
        logging.info('Download finished %s', str(datetime.now()))
        logging.info('End of processing %s \n', str(datetime.now()))


def make_request(token, userid, data):
    headers = {
        'Origin': 'https://apps.sentinel-hub.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,sl;q=0.8',
        'Authorization': 'Bearer ' + token + '',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://apps.sentinel-hub.com/mosaic-hub/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Connection': 'keep-alive',
    }

    # name = '"Jan_test_order_JP2_v7"'
    # imageFormat = '"JP2"'
    # resolution = '"R60m"'
    # coordsys = '"UTM"'
    # bands = '{"bands":["B02","B03","B04","B08","B01","B05","B8A","B06","B07", ' \
    #         '"B12","B11","AOT","CLOUD","SNOW","INDEX","SCENE", "MEDOID_MOS",' \
    #         '"SUN_ZENITH","SUN_AZIMUTH", "VIEW_ZENITH_MEAN",' \
    #         '"VIEW_AZIMUTH_MEAN"]}'
    #
    # data = '{"name":' + name + ',' + '"status":"ORDER_PLACED","created":' + \
    #        '""' + ',"imageFormat":' + imageFormat + \
    #        ',"resolution":' + resolution + ',"coordinateSystem":' + coordsys + ',"additionalData":' + bands + ',"userId":"' + userid + '","areaOfInterest":{"crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:EPSG::4326"}},"type":"MultiPolygon","coordinates":[[[[6.043073,50.128052],[6.242751,49.902226],[6.18632,49.463803],[5.897759,49.442667],[5.674052,49.529484],[5.782417,50.090328],[6.043073,50.128052]]]]},"startDate":"2018-06-01T00:00:00Z","temporalPeriod":"MONTH"}'

    response = requests.post(
        'https://services-s2gm.sentinel-hub.com/order/orders', headers=headers,
        data=data)

    # response.raise_for_status()
    log_request(response.status_code)
    request_id = response.json()['id']
    order_name = response.json()['name']
    temporal_period = response.json()['temporalPeriod']
    resolution = response.json()['resolution']

    start_date = datetime.strptime(response.json()['startDate'][0:10], "%Y-%m-%d").date()

    if temporal_period == 'DAY':
        end_date = start_date
    elif temporal_period == 'TENDAYS':
        end_date = start_date + timedelta(days=10)
    elif temporal_period == 'MONTH':
        end_date = datetime.strptime(str(start_date.year) + str(start_date.month) + str(calendar.monthrange(start_date.year, start_date.month)[1]), "%Y%m%d").date()
    elif temporal_period == 'QUARTER':
        end_date = datetime.strptime(
            str(start_date.year) + str(start_date.month + 2) + str(
                calendar.monthrange(start_date.year, start_date.month)[1]),
            "%Y%m%d").date()
    else:
        if start_date.month + 11 > 12:
            end_date = datetime.strptime(str(start_date.year + 1) + str(start_date.month -1 ) + str(calendar.monthrange(start_date.year + 1, start_date.month - 1)[1]),"%Y%m%d").date()
        else:
            end_date = datetime.strptime(
                str(start_date.year) + str(start_date.month + 11) + str(
                    calendar.monthrange(start_date.year, start_date.month)[1]),
                "%Y%m%d").date()

    with open('variables/request_variables.pkl', 'wb') as f:
        pickle.dump([request_id, order_name, start_date, end_date, temporal_period, resolution], f)
    return request_id, order_name, start_date, end_date, temporal_period, resolution


def check_processing_status(token, request_id):
    '''
    This module monitors the processing status and defines a trigger variable
    for the next processing steps
    '''
    ## write code for status monitoring and define a trigger value for later download

    headers = {
        'Origin': 'https://apps.sentinel-hub.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,sl;q=0.8',
        'Authorization': 'Bearer ' + token + '',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://apps.sentinel-hub.com/mosaic-hub/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Connection': 'keep-alive',
    }

    done = False
    count = 0
    while not done:
        response_status = requests.get(
            'https://services-s2gm.sentinel-hub.com/order/orders/' + request_id,
            headers=headers)
        # request_id = response_status.json()['id']
        status = response_status.json()['status']
        if status == 'FINISHED':
            done = True
            log_processing(request_id, done, count)
        else:
            time.sleep(10)
            log_processing(request_id, done, count)
            count += 1
    return done


def downloader(start, running, finished, download_folder, request_id, token, start_date, end_date, temporal_period, resolution, order_name):
    '''
    This module downloads all requested data
    :return:
    '''
    # write data downloader

    headers = {
        'Origin': 'https://apps.sentinel-hub.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,sl;q=0.8',
        'Authorization': 'Bearer ' + token + '',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://apps.sentinel-hub.com/mosaic-hub/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Connection': 'keep-alive',
    }

    order_list = requests.get(
        'https://services-s2gm.sentinel-hub.com/mosaic/index/v1/mosaic/',
        headers=headers)
    order_list_text = order_list.text
    split_order_list_text = order_list_text.split(',{"@id"')
    final_order_list = []
    for x in range(len(split_order_list_text)):
        if x == 0:
            final_order_list.append(split_order_list_text[x])
        else:
            final_order_list.append('{"@id"' + split_order_list_text[x])
    for entry in final_order_list:
        if entry.find(request_id) != -1:
            my_order = entry
    mosaic_id = my_order.split('"id":')[1].split(',', 1)[0]

    os.mkdir(download_folder + 'S2GM_' + temporal_period[0].upper() + resolution[1:3] + '_' + start_date.strftime('%Y%m%d') + '_'  + end_date.strftime('%Y%m%d') + '_' + order_name + '_STD_v0.1.0_' + mosaic_id + '/')
    os.mkdir(
        download_folder + 'S2GM_' + temporal_period[0].upper() + resolution[
                                                                 1:3] + '_' + start_date.strftime(
            '%Y%m%d') + '_' + end_date.strftime(
            '%Y%m%d') + '_' + order_name + '_STD_v0.1.0_' + mosaic_id + '/' + order_name + '/')
    download_folder = download_folder + 'S2GM_' + temporal_period[0].upper() + resolution[
                                                                 1:3] + '_' + start_date.strftime(
            '%Y%m%d') + '_' + end_date.strftime(
            '%Y%m%d') + '_' + order_name + '_STD_v0.1.0_' + mosaic_id + '/' + order_name + '/'

    url = ''
    start = True
    log_download(start, running, finished, url)
    running = True
    log_download(start, running, finished, url)
    tile_number = int(requests.get(
        'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/maxDownloadSequence',
        headers=headers).json())
    for count in range(1, tile_number + 1):
        data_list = requests.get(
            'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/sequence/' + str(
                count) + '/metadata', headers=headers).json()
        for file in data_list['files']:
            url = 'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/sequence/1?filename=' + file
            file_response = requests.get(url, headers=headers, stream=True)
            out_filename_long = data_list['namingMap'][file]
            out_filename = out_filename_long.split('/')[len(out_filename_long.split('/'))-1]
            with open(download_folder + out_filename, 'wb') as out_file:
                shutil.copyfileobj(file_response.raw, out_file)
            del file_response
            # log_download(start, running, finished, url)
            print(file + ' - ' + out_filename)

    running = False
    finished = True
    log_download(start, running, finished, url)


def control(TOKEN, USERID, DOWNLOAD_FOLDER, data):
    request_id, order_name, start_date, end_date, temporal_period, resolution = make_request(TOKEN, USERID, data)
    done = check_processing_status(TOKEN, request_id)
    start = False
    running = False
    finished = False
    if done:
        downloader(start, running, finished, DOWNLOAD_FOLDER,
                   request_id, TOKEN, start_date, end_date,
                   temporal_period, resolution, order_name)


if __name__ == '__main__':
    # CLI = argparse.ArgumentParser()
    # CLI.add_argument(
    #     "--TOKEN",# name on the CLI - drop the `--` for positional/required parameters
    #     nargs="1",  # 0 or more values expected => creates a list
    #     type=str,
    #     default='', # default if nothing is provided
    #     help='Bearer Token needed'
    # )
    # CLI.add_argument(
    #     "--USERID",# name on the CLI - drop the `--` for positional/required parameters
    #     nargs="1",  # 0 or more values expected => creates a list
    #     type=str,
    #     default='', # default if nothing is provided
    #     help='user ID needed'
    # )
    # CLI.add_argument(
    #     "--DOWNLOAD_FOLDER",# name on the CLI - drop the `--` for positional/required parameters
    #     nargs="1",  # 0 or more values expected => creates a list
    #     type=str,
    #     default='', # default if nothing is provided
    #     help='Set download folder'
    # )
    # # parse the command line
    # args = CLI.parse_args()

    control(TOKEN, USERID, DOWNLOAD_FOLDER, data)