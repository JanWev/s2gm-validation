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


def check_processing_status(token, request_id, prod_id):
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
        if response_status.status_code == 401:
            print('Login not possible. Get new bearer token from Mosaic Hub')
            done = True
        else:
            status = response_status.json()['status']
            if status == 'FINISHED':
                done = True
                log_processing(request_id, done, count)
            else:
                time.sleep(120)
                log_processing(request_id, done, count)
                count += 1

    if prod_id < 10:
        file = 'variables/order_status_variables_0' + str(prod_id) + '.pkl'
    else:
        file = 'variables/order_status_variables_' + str(prod_id) + '.pkl'
    with open(file, 'wb') as f:
        pickle.dump(done, f)
    return response_status.status_code

def run(TOKEN, prod_id):
    if prod_id < 10:
        file = './variables/request_variables_0' + str(prod_id) + '.pkl'
    else:
        file = './variables/request_variables_' + str(prod_id) + '.pkl'
    with open(file, 'rb') as f:
        request_id = pickle.load(f)[0]
    if request_id == '':
        pass
    else:
        status_code = check_processing_status(TOKEN, request_id, prod_id)
        return status_code


if __name__ == '__main__':
    status_code = run(TOKEN, prod_id)