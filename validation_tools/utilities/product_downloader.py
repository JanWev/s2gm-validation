# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import os
import requests
import logging
from datetime import datetime
import shutil
import pickle

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def log_download(start, running, finished, url):
    logging.basicConfig(filename='./logs/execution.log', filemode='a',
                        level=logging.DEBUG)
    if start and not finished and not running:
        logging.info('Download started  : %s', str(datetime.now()))
        # logging.debug('Requested tests by the user: %s', str(''))

    if start and not finished and running:
        logging.debug('Downloading %s: %s', url, str(datetime.now()))

    if start and finished:
        logging.info('Download finished %s', str(datetime.now()))
        logging.info('End of processing %s \n', str(datetime.now()))

def downloader(start, running, finished, download_folder, request_id, token, start_date, end_date, temporal_period,
               resolution, order_name, prod_id, list_number, version_number):
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
        'https://services-s2gm.sentinel-hub.com/mosaic/index/v1/mosaic/?viewtoken=' + str(list_number),
        headers=headers)
    order_list_text = order_list.text
    split_order_list_text = order_list_text.split(',{"@id"')
    final_order_list = []
    for x in range(len(split_order_list_text)):
        if x == 0:
            final_order_list.append(split_order_list_text[x])
        else:
            final_order_list.append('{"@id"' + split_order_list_text[x])
    my_order = ''
    for entry in final_order_list:
        if entry.find(request_id) != -1:
            my_order = entry
    if my_order == '':
        print(order_name + ' product not found in current list')
        status_code = 900
        return status_code
    else:
        mosaic_id = my_order.split('"id":')[1].split(',', 1)[0]
        if prod_id < 10:
            file = download_folder + 'variables/request_variables_0' + str(prod_id) + '.pkl'
        else:
            file = download_folder + 'variables/request_variables_' + str(prod_id) + '.pkl'
        with open(file, 'wb') as f:
            pickle.dump([request_id, order_name, start_date, end_date, temporal_period, resolution, mosaic_id], f)

        parent_dir = download_folder + 'R' + start_date.strftime('%Y%m%d') + temporal_period[0].upper() + \
                     resolution[1:3] + '_'  + order_name + '_STD_v' + version_number + '_' + mosaic_id + '/'
        child_dir = download_folder + 'R' + start_date.strftime('%Y%m%d') + temporal_period[0].upper() + \
                    resolution[1:3] + '_'  + order_name + '_STD_v' + version_number + '_' + mosaic_id + '/' + \
                    order_name + '/'
        if not os.path.exists(parent_dir):
            os.mkdir(parent_dir)
        if not os.path.exists(child_dir):
            os.mkdir(child_dir)
        download_folder = child_dir

        url = ''
        start = True
        log_download(start, running, finished, url)
        running = True
        log_download(start, running, finished, url)
        status_code = requests.get(
            'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/maxDownloadSequence',
            headers=headers).status_code
        if status_code == 404:
            print('File not available')
            return status_code
        else:
            tile_number = int(requests.get(
                'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/maxDownloadSequence',
                headers=headers).json())
            for count in range(1, tile_number + 1):
                data_list = requests.get(
                    'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/sequence/' + str(
                        count) + '/metadata', headers=headers).json()
                for file in data_list['files']:
                    url = 'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/sequence/' + str(
                        count) + '?filename=' + file
                    file_response = requests.get(url, headers=headers, stream=True)
                    out_filename_long = data_list['namingMap'][file]
                    out_filename = out_filename_long.split('/')[len(out_filename_long.split('/'))-1]
                    with open(download_folder + out_filename, 'wb') as out_file:
                        shutil.copyfileobj(file_response.raw, out_file)
                    del file_response
                    print(file + ' - ' + out_filename)

            running = False
            finished = True
            log_download(start, running, finished, url)
            return status_code


def run(TOKEN, DOWNLOAD_FOLDER, prod_id, list_number, version_number):
    if prod_id < 10:
        file = DOWNLOAD_FOLDER + 'variables/request_variables_0' + str(prod_id) + '.pkl'
    else:
        file = DOWNLOAD_FOLDER + 'variables/request_variables_' + str(prod_id) + '.pkl'
    with open(file, 'rb') as f:
        size = len(pickle.load(f))
        if size == 6:
            with open(file, 'rb') as f:
                [request_id, order_name, start_date, end_date, temporal_period, resolution] = pickle.load(f)
        else:
            with open(file, 'rb') as f:
                [request_id, order_name, start_date, end_date, temporal_period, resolution, order_number] = pickle.load(f)
    start = False
    running = False
    finished = False
    if request_id == '':
        status_code = 900
        return status_code
    else:

        status_code = downloader(start, running, finished, DOWNLOAD_FOLDER,
                             request_id,TOKEN, start_date, end_date,
                             temporal_period, resolution, order_name, prod_id, list_number, version_number)
        return status_code


if __name__ == '__main__':
    run(TOKEN, DOWNLOAD_FOLDER, prod_id, list_number, version_number)
