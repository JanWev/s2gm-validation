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

    parent_dir = download_folder + 'S2GM_' + temporal_period[0].upper() + resolution[1:3] + '_' + start_date.strftime('%Y%m%d') + '_'  + end_date.strftime('%Y%m%d') + '_' + order_name + '_STD_v0.1.0_' + mosaic_id + '/'
    child_dir = download_folder + 'S2GM_' + temporal_period[0].upper() + resolution[
                                                                 1:3] + '_' + start_date.strftime(
            '%Y%m%d') + '_' + end_date.strftime(
            '%Y%m%d') + '_' + order_name + '_STD_v0.1.0_' + mosaic_id + '/' + order_name + '/'
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
            print(file + ' - ' + out_filename)

    running = False
    finished = True
    log_download(start, running, finished, url)


def run(TOKEN, DOWNLOAD_FOLDER):
    with open('./variables/request_variables.pkl', 'rb') as f:
        [request_id, order_name, start_date, end_date, temporal_period,
         resolution] = pickle.load(f)
    start = False
    running = False
    finished = False
    downloader(start, running, finished, DOWNLOAD_FOLDER, request_id, TOKEN,
               start_date, end_date, temporal_period, resolution, order_name)


if __name__ == '__main__':
    run(TOKEN, DOWNLOAD_FOLDER)