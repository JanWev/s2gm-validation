# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import requests
import logging
from datetime import datetime
import time
import pickle

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'


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

    with open('variables/order_status_variables.pkl', 'wb') as f:
        pickle.dump(done, f)

def run(TOKEN):
    with open('./variables/request_variables.pkl', 'rb') as f:
        request_id = pickle.load(f)[0]
    check_processing_status(TOKEN, request_id)



if __name__ == '__main__':
    run(TOKEN)