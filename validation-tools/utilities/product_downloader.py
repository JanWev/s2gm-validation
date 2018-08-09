# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import requests
import logging
from datetime import datetime
import random

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

GRANULE_LIST = ['29TFJ', ]

def define_request_parameters():
    #4 fix requests
    data_01 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 10}'
    data_02 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "YEAR", "resolution": 20}'
    data_03 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "QUARTER", "resolution": 10}'
    data_04 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 60}'

    id = random.sample(GRANULE_LIST)


def log():
    logging.basicConfig(filename='execution.log', filemode='a',level=logging.DEBUG)
    logging.info('Request : %s', str(datetime.now()))
    logging.debug('Requested tests by the user: %s', str(tests))
    logging.info('\n')

def make_request():
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    data = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 10}'

    response = requests.post('http://services-s2gm.sentinel-hub.com/mosaic/add', headers=headers, data=data)
    #response.raise_for_status()
    log(response.status_code)

def main():
    make_request()

if __name__ == '__main__':
    main()