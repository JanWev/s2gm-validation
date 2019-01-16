# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import requests
import logging
from datetime import datetime, timedelta
import calendar
import pickle
from .static_parameters import DOWNLOAD_FOLDER

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

logging.getLogger("requests").setLevel(logging.WARNING)

def log_request(html_status):
    logging.basicConfig(filename='./logs/execution.log', filemode='a',
                        level=logging.DEBUG)
    logging.info('Request data at mosaic hub  : %s', str(datetime.now()))
    logging.debug('HTML status: %s', str(html_status))


def make_request(DOWNLOAD_FOLDER, token, data, prod_id):
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

    response = requests.post(
        'https://services-s2gm.sentinel-hub.com/order/orders', headers=headers,
        data=data)

    # log_request(response.status_code)
    if response.status_code == 201:
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
    else:
        request_id = ''
        order_name = ''
        start_date = ''
        end_date = ''
        temporal_period = ''
        resolution = ''

    if prod_id < 10:
        file = DOWNLOAD_FOLDER + 'variables/request_variables_0' + str(prod_id) + '.pkl'
    else:
        file = DOWNLOAD_FOLDER + 'variables/request_variables_' + str(prod_id) + '.pkl'
    with open(file, 'wb') as f:
        pickle.dump([request_id, order_name, start_date, end_date, temporal_period, resolution], f)
    return response.status_code

def run(DOWNLOAD_FOLDER, TOKEN, data, prod_id):
    status_code = make_request(DOWNLOAD_FOLDER, TOKEN, data, prod_id)
    return status_code

if __name__ == '__main__':
    run(DOWNLOAD_FOLDER, TOKEN, data, prod_id)