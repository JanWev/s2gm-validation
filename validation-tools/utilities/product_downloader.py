# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import requests
import logging
from datetime import datetime
import random
import pickle
import time
import shutil
import json

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

GRANULE_LIST = ['T34UFB', 'T34UFA', 'T35TNN', 'T35TNM', 'T35TNL', 'T34UFV', 'T35TQM', 'T35TPN', 'T35TPM', 'T35TPL', 'T35ULV', 'T35ULB', 'T35ULA', 'T34UGE', 'T34UEV', 'T34UDV', 'T35UMV', 'T35UMA', 'T33UWV', 'T33UWU', 'T33UWT', 'T31UFV', 'T33UXV', 'T33UXU', 'T33UXT', 'T33UXA', 'T35UPP', 'T35UNP', 'T35UMP', 'T35TQN', 'T31UFU', 'T31UEU', 'T34TEN', 'T34TEM', 'T33SVB', 'T33SVA', 'T33SUC', 'T33SUB', 'T34VDJ', 'T34VDH', 'T33SWA', 'T33SVC', 'T32TNK', 'T32TMK', 'T32SNJ', 'T32SMJ', 'T33STC', 'T33STB', 'T32SQH', 'T32SQG', 'T34UEF', 'T34UDG', 'T35VNC', 'T35VMC', 'T34UFG', 'T34UFF', 'T34UFE', 'T34UEG', 'T34VFJ', 'T34VFH', 'T34VEJ', 'T34VEH', 'T35VLD', 'T35VLC', 'T35UNB', 'T35UMB', 'T33SXC', 'T33SWD', 'T33SWC', 'T33SWB', 'T33TUF', 'T33TTG', 'T33TTF', 'T33SXD', 'T32TQM', 'T32TQL', 'T32TPR', 'T32TPQ', 'T32TQR', 'T32TQQ', 'T32TQP', 'T32TQN', 'T33TXF', 'T33TXE', 'T33TWG', 'T33TWF', 'T34TBL', 'T34TBK', 'T33TYF', 'T33TYE', 'T33TVE', 'T33TUJ', 'T33TUH', 'T33TUG', 'T33TWE', 'T33TVH', 'T33TVG', 'T33TVF', 'T34TCS', 'T33UYP', 'T33TYN', 'T34TBM', 'T34TES', 'T34TDT', 'T34TDS', 'T34TCT', 'T33TVL', 'T33TVK', 'T33TUL', 'T33TUK', 'T33TWH', 'T33TVJ', 'T33TYM', 'T33TXM', 'T32TNQ', 'T32TNP', 'T32TMS', 'T32TMR', 'T32TPP', 'T32TPN', 'T32TPM', 'T32TNR', 'T34UDU', 'T34UCU', 'T34TFT', 'T34TET', 'T32TMQ', 'T32TMP', 'T34UFU', 'T34UEU', 'T35SKD', 'T35SMD', 'T35SLD', 'T34SCJ', 'T35SMB', 'T35SLB', 'T35SMC', 'T35SLC', 'T34TGK', 'T34TFK', 'T34SGJ', 'T34SGH', 'T35TLE', 'T35TKE', 'T35SKC', 'T35SKB', 'T35SKU', 'T34SGE', 'T34SGD', 'T35SMV', 'T35SMU', 'T35SLV', 'T35SLU', 'T35SKV', 'T35SNA', 'T35SMA', 'T35SLA', 'T35SNB', 'T35SPA', 'T35SNV', 'T35SKA', 'T34SGF', 'T32UPV', 'T32UPU', 'T32UPE', 'T32UPD', 'T33UUT', 'T32UQE', 'T32UQD', 'T32UQC', 'T32UNU', 'T32UNE', 'T32UND', 'T32UNC', 'T32UPC', 'T32UPB', 'T32UPA', 'T32UNV', 'T34SFF', 'T34SEJ', 'T34SEH', 'T34SEG', 'T34SGG', 'T34SFJ', 'T34SFH', 'T34SFG', 'T33UVU', 'T33UVT', 'T33UUV', 'T33UUU', 'T34SEF', 'T34SDH', 'T34SDG', 'T33UVV', 'T30UUE', 'T29UQV', 'T29VNE', 'T29VND', 'T30UXF', 'T30UXE', 'T30UXD', 'T30UXC', 'T30UYD', 'T30UYC', 'T30UYB', 'T30UXG', 'T30UWD', 'T30UWC', 'T30UWB', 'T30UVG', 'T30UXB', 'T30UWG', 'T30UWF', 'T30UWE', 'T31UCT', 'T30VWK', 'T30VWJ', 'T30VWH', 'T31UDU', 'T31UDT', 'T31UCV', 'T31UCU', 'T30VUK', 'T30VUJ', 'T30VUH', 'T30UYE', 'T30VVK', 'T30VVJ', 'T30VVH', 'T30VUL', 'T30VXM', 'T30VWM', 'T30VWN', 'T30VXN', 'T29UQS', 'T29UQR', 'T30VVL', 'T30VWL', 'T34WFV', 'T34WFU', 'T34WFT', 'T34WFA', 'T33VXC', 'T34VCJ', 'T34VDK', 'T34VCK', 'T30UVB', 'T30UVA', 'T30UUG', 'T30UUF', 'T30UVF', 'T30UVE', 'T30UVD', 'T30UVC', 'T29VPE', 'T29VPD', 'T29VPC', 'T29UQT', 'T30UUD', 'T30UUC', 'T30UUB', 'T30UUA', 'T33WXR', 'T33WXQ', 'T33WXP', 'T33WXN', 'T34VCN', 'T34VCM', 'T34VCL', 'T33WXS', 'T33WWN', 'T33WWM', 'T33WVP', 'T33WVN', 'T33WXM', 'T33WWR', 'T33WWQ', 'T33WWP', 'T34WEB', 'T34WEA', 'T34WDV', 'T34WDU', 'T34WEV', 'T34WEU', 'T34WET', 'T34WES', 'T34VDR', 'T34VCR', 'T34VCQ', 'T34VCP', 'T34WDT', 'T34WDS', 'T34WDB', 'T34WDA', 'T33VVJ', 'T33VVH', 'T33VVG', 'T33VVF', 'T33VWD', 'T33VWC', 'T33VVL', 'T33VVK', 'T33VUK', 'T33VUJ', 'T33VUH', 'T33VUG', 'T33VVE', 'T33VVD', 'T33VVC', 'T33VUL', 'T33VXH', 'T33VXG', 'T33VXF', 'T33VXE', 'T33WVM', 'T33VXL', 'T33VXK', 'T33VXJ', 'T33VWH', 'T33VWG', 'T33VWF', 'T33VWE', 'T33VXD', 'T33VWL', 'T33VWK', 'T33VWJ', 'T31TDF', 'T31TCG', 'T31TCF', 'T31TCE', 'T31SED', 'T31SDD', 'T31TFE', 'T31TEE', 'T31SBC', 'T30TYM', 'T30TYL', 'T30TYK', 'T31TBG', 'T31TBF', 'T31TBE', 'T31SBD', 'T32VPR', 'T32VPQ', 'T32VPP', 'T32VPN', 'T33VUF', 'T33VUE', 'T33VUD', 'T32WPS', 'T30SVE', 'T31SCD', 'T31SCC', 'T31TDE', 'T32VPM', 'T32VPL', 'T32VPK', 'T30SWE', 'T30SXJ', 'T30SXH', 'T30SXG', 'T30SXF', 'T30TTK', 'T30SYJ', 'T30SYH', 'T30SYG', 'T30SVJ', 'T30SVH', 'T30SVG', 'T30SVF', 'T30SWJ', 'T30SWH', 'T30SWG', 'T30SWF', 'T30TWL', 'T30TWK', 'T30TVP', 'T30TVN', 'T30TXM', 'T30TXL', 'T30TXK', 'T30TWM', 'T30TUN', 'T30TUM', 'T30TUL', 'T30TUK', 'T30TVM', 'T30TVL', 'T30TVK', 'T30TUP', 'T29SQD', 'T29SQC', 'T29SQB', 'T29SQA', 'T29TMJ', 'T29TMH', 'T29TMG', 'T29SQV', 'T35TNK', 'T35TMN', 'T35TMM', 'T35TML', 'T35ULP', 'T35TQL', 'T35TQK', 'T35TPK', 'T30STJ', 'T30STH', 'T30STG', 'T30STF', 'T30SUJ', 'T30SUH', 'T30SUG', 'T30SUF', 'T29TPJ', 'T29TPH', 'T29TNJ', 'T29TNH', 'T30STE', 'T29TQJ', 'T29TQH', 'T29TQE', 'T32UMV', 'T32UMU', 'T32ULV', 'T32ULU', 'T32TNL', 'T32TMN', 'T32TMM', 'T32TML', 'T32TLP', 'T32TLN', 'T31UGP', 'T31UFP', 'T32TLT', 'T32TLS', 'T32TLR', 'T32TLQ', 'T32UMC', 'T32UMB', 'T32UMA', 'T32ULE', 'T32UNB', 'T32UNA', 'T32UME', 'T32UMD', 'T31UGU', 'T31UGT', 'T32TNN', 'T32TNM', 'T32ULD', 'T32ULC', 'T32TMT', 'T31UGV', 'T31TFH', 'T31TEN', 'T31TEM', 'T31TEL', 'T31TFM', 'T31TFL', 'T31TFK', 'T31TFJ', 'T31TDN', 'T31TDM', 'T31TDL', 'T31TDK', 'T31TEK', 'T31TEJ', 'T31TEH', 'T31TEG', 'T31UDP', 'T31UCS', 'T31UCR', 'T31UCQ', 'T31UEQ', 'T31UEP', 'T31UDR', 'T31UDQ', 'T31TGK', 'T31TGJ', 'T31TGH', 'T31TFN', 'T31UCP', 'T31TGN', 'T31TGM', 'T31TGL', 'T30UUV', 'T30UUU', 'T30TYT', 'T30TYS', 'T30UWU', 'T30UWA', 'T30UVV', 'T30UVU', 'T30TXT', 'T30TXS', 'T30TXR', 'T30TXQ', 'T30TYR', 'T30TYQ', 'T30TYP', 'T30TYN', 'T31TCM', 'T31TCL', 'T31TCK', 'T31TCJ', 'T31TDJ', 'T31TDH', 'T31TDG', 'T31TCN', 'T30UXV', 'T30UXU', 'T30UXA', 'T30UWV', 'T31TCH', 'T30UYV', 'T30UYU', 'T30UYA', 'T33UUQ', 'T32UQV', 'T32UQB', 'T32UQA', 'T33UVS', 'T33UVR', 'T33UUS', 'T33UUR', 'T35VNE', 'T35VND', 'T35VMG', 'T35VMF', 'T34VEK', 'T34VEL', 'T35VNG', 'T35VNF', 'T30TWP', 'T30TWN', 'T30TVT', 'T30TUT', 'T30TXP', 'T30TXN', 'T30TWT', 'T30TWS', 'T33UXS', 'T33UXR', 'T33UWS', 'T33UWR', 'T34UCV', 'T34UCA', 'T33UYR', 'T33UYQ', 'T29UMU', 'T29UMT', 'T29UMS', 'T29UMA', 'T29UNT', 'T29UNB', 'T29UNA', 'T29UMV', 'T33UVB', 'T33UVA', 'T33VUC', 'T33UUB', 'T29ULT', 'T28UGC', 'T33UWB', 'T33UWA', 'T35VLE', 'T34VFM', 'T34VFL', 'T34VFK', 'T35VME', 'T35VMD', 'T35VLG', 'T35VLF', 'T29UPB', 'T29UPA', 'T29UNV', 'T29UNU', 'T29UQU', 'T29UPV', 'T29UPU', 'T29UPT', 'T35TMG', 'T35TMF', 'T35TLJ', 'T35TLH', 'T35TNH', 'T35TNG', 'T35TMJ', 'T35TMH', 'T34TGP', 'T34TGN', 'T34TGM', 'T34TGL', 'T35TLG', 'T35TLF', 'T35TKG', 'T35TKF', 'T32VNH', 'T32UNG', 'T32UNF', 'T32UMG', 'T33UUA', 'T32UPG', 'T32UPF', 'T32VPH', 'T32VMJ', 'T32VMH', 'T35TPJ', 'T35TNJ', 'T32UMF', 'T32VPJ', 'T32VNK', 'T32VNJ', 'T32ULA', 'T31UGS', 'T31UGR', 'T31UGQ', 'T33TWL', 'T33TWK', 'T33TWJ', 'T32ULB', 'T31UET', 'T31UES', 'T31UER', 'T31UDS', 'T31UFT', 'T31UFS', 'T31UFR', 'T31UFQ', 'T34TFL', 'T34TCR', 'T34TCQ', 'T34TCP', 'T34TFQ', 'T34TFP', 'T34TFN', 'T34TFM', 'T33TXL', 'T33TXK', 'T33TXJ', 'T33TXH', 'T33TYL', 'T33TYK', 'T33TYJ', 'T33TYH', 'T32TNS', 'T34TEL', 'T34TEK', 'T34TDN', 'T32TQS', 'T32TPT', 'T32TPS', 'T32TNT', 'T34TCM', 'T34TCL', 'T34TCK', 'T34SDJ', 'T34TDM', 'T34TDL', 'T34TDK', 'T34TCN', 'T33UVQ', 'T33UVP', 'T33UUP', 'T33TXN', 'T33UXQ', 'T33UXP', 'T33UWQ', 'T33UWP', 'T33TUN', 'T33TUM', 'T32UQU', 'T32TQT', 'T33TWN', 'T33TWM', 'T33TVN', 'T33TVM', 'T29TPF', 'T29TPE', 'T29TNG', 'T29TNF', 'T30TTL', 'T29TQG', 'T29TQF', 'T29TPG', 'T29SPB', 'T29SPA', 'T29SND', 'T29SNC', 'T29TNE', 'T29TME', 'T29SPD', 'T29SPC', 'T35TLK', 'T34UGU', 'T34TGT', 'T34TGS', 'T35TMK', 'T35TLN', 'T35TLM', 'T35TLL', 'T34TER', 'T34TEQ', 'T34TDR', 'T30TTM', 'T34TGR', 'T34TGQ', 'T34TFS', 'T34TFR', 'T34UDC', 'T34UDB', 'T34UDA', 'T34UCF', 'T34UEA', 'T34UDF', 'T34UDE', 'T34UDD', 'T33UYV', 'T33UYU', 'T33UYT', 'T33UYS', 'T34UCE', 'T34UCD', 'T34UCC', 'T34UCB', 'T29SMB', 'T29SMA', 'T34UGB', 'T34UGA', 'T29SNB', 'T29SNA', 'T29SMD', 'T29SMC', 'T34UEE', 'T34UED', 'T34UEC', 'T34UEB', 'T34UFD', 'T34UFC']
RANDOMIZE = False
START = False
RUNNING = False
FINISHED = False
DOWNLOAD_FOLDER = 'K:/S2GM/S2GM_mosaics/v0.6.5/Python_downloads/'

def define_request_parameters():
    #4 fix requests
    data_01 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 10}'
    data_02 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "YEAR", "resolution": 20}'
    data_03 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "QUARTER", "resolution": 10}'
    data_04 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 60}'

    if RANDOMIZE:
        id = random.sample(GRANULE_LIST, 11)
        with open('ids.pkl', 'wb') as f:
            pickle.dump(id, f)
    else:
        try:
            with open('ids.pkl', 'rb') as f:
                id = pickle.load(f)
        except FileNotFoundError:
            print('IDs do not exist, start randomizing')
            id = random.sample(GRANULE_LIST, 11)
            with open('ids.pkl', 'wb') as f:
                pickle.dump(id, f)

def log_request(html_status):
    logging.basicConfig(filename='..\execution.log', filemode='a',level=logging.DEBUG)
    logging.info('Request data at mosaic hub  : %s', str(datetime.now()))
    logging.debug('HTML status: %s', str(html_status))


def log_processing(request_id, done, count):
    logging.basicConfig(filename='..\execution.log', filemode='a',level=logging.DEBUG)
    if count == 0:
        logging.info('Processing has started  : %s', str(datetime.now()))
    if done:
        logging.info('Processing of request %s in S2GM hub is finished: %s', request_id, str(datetime.now()))
        logging.info('Ready for download %s', str(datetime.now()))
    else:
        logging.debug('Processing of request %s not finished yet: %s', request_id, str(datetime.now()))

def log_download(start, running, finished, url):
    logging.basicConfig(filename='..\execution.log', filemode='a',level=logging.DEBUG)
    print('Start value: %s \n', str(start))
    print('Stop value: %s \n', str(finished))
    if start and not finished:
        logging.info('Download started  : %s', str(datetime.now()))
        #logging.debug('Requested tests by the user: %s', str(''))

    if start and not finished and running:
        logging.debug('Downloading %s: %s', url, str(datetime.now()))

    if start and finished:
        logging.info('Download finished %s', str(datetime.now()))
        logging.info('End of processing %s \n', str(datetime.now()))


def make_request():
    ## old version uwe
    # headers = {
    #     'Cache-Control': 'no-cache',
    #     'Content-Type': 'application/json',
    # }
    #
    # data = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 10}'
    #
    # response = requests.post('http://services-s2gm.sentinel-hub.com/mosaic/add', headers=headers, data=data)


    ## new version from rok

    token = 'eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MjBhYjE5ZS0xMjFhLTQ3ZWMtYWQ3ZS0yOTMwNmE0YzIyMzkiLCJhdWQiOiJjNTI1NDQ0Yy02YmQ0LTQyOTAtYjU2Zi0xMWI3OTI0OTE0NjUiLCJqdGkiOiI5ZTgxYjk3OGI4YzBmZjM5NDAwNmJmZTAyYjdjYThhMyIsImV4cCI6MTUzNDE3Mjk5OSwibmFtZSI6IkphbiBXZXZlcnMiLCJlbWFpbCI6Imphbi53ZXZlcnNAYnJvY2ttYW5uLWNvbnN1bHQuZGUiLCJnaXZlbl9uYW1lIjoiSmFuIiwiZmFtaWx5X25hbWUiOiJXZXZlcnMiLCJhY2NvdW50Ijp7InR5cGUiOjEwMDB9fQ.eaw1lQdbGh3uKh1z-E_5f4FZmSy5vlkg-Q9Z6fXBCV6AyaT-DQCxpUpY6vmbkdgQrK2kRBM0KU2AyyYWWBARmQpK7ikr_80Qp55l6pT_7m-ACejPhq9nsIfGiRPuIOR7sARl0OkQuoBEVPwcbuW4VotuDVAmajOXlTReAa7kAEeUd32qggp08-7M3XIOcYHpLOzCJSirNv0mdpPVx3z6RSx-wBFw8pxWPav4OmQCirp5s1epQXuzc4I7aXqrUyJRsalop3IwzvEN4UOUezdddb3rPqfUMlMRHYNPzeE2NBt75v59kBbwPcrIk89XxQIag-ef4-6mNXCrlVX_3yNO9g'
    userid = '820ab19e-121a-47ec-ad7e-29306a4c2239'

    headers = {
        'Origin': 'https://apps.sentinel-hub.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,sl;q=0.8',
        'Authorization': 'Bearer ' + token +'',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://apps.sentinel-hub.com/mosaic-hub/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Connection': 'keep-alive',
    }

    name = '"Jan_test_order_JP2_v7"'
    imageFormat = '"JP2"'
    resolution = '"R60m"'
    coordsys = '"UTM"'
    # + created.replace(' ','T') +

    data = '{"name":' + name + ',' + '"status":"ORDER_PLACED","created":' +\
           '""' +',"imageFormat":' + imageFormat + \
           ',"resolution":' + resolution + ',"coordinateSystem":' + coordsys + ',"additionalData":{"bands":["B02","B03","B04","B08","B01","B05","B8A","B06","B07","B12","B11","AOT","CLOUD","SNOW","INDEX","SCENE","MEDOID_MOS","SUN_ZENITH","SUN_AZIMUTH","VIEW_ZENITH_MEAN","VIEW_AZIMUTH_MEAN"]},"userId":"' + userid + '","areaOfInterest":{"crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:EPSG::4326"}},"type":"MultiPolygon","coordinates":[[[[6.043073,50.128052],[6.242751,49.902226],[6.18632,49.463803],[5.897759,49.442667],[5.674052,49.529484],[5.782417,50.090328],[6.043073,50.128052]]]]},"startDate":"2018-06-01T00:00:00Z","temporalPeriod":"MONTH"}'

    response = requests.post(
        'https://services-s2gm.sentinel-hub.com/order/orders', headers=headers,
        data=data)

    #response.raise_for_status()
    log_request(response.status_code)
    request_id = response.json()['id']
    return token, userid, request_id

def check_processing_status(token, userid, request_id):
    '''
    This module monitors the processing status and defines a trigger variable
    for the next processing steps
    '''
    ## write code for status monitoring and define a trigger value for later download

    headers = {
        'Origin': 'https://apps.sentinel-hub.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,sl;q=0.8',
        'Authorization': 'Bearer ' + token +'',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://apps.sentinel-hub.com/mosaic-hub/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Connection': 'keep-alive',
    }

    done = False
    count = 0
    while not done:
        response_status = requests.get('https://services-s2gm.sentinel-hub.com/order/orders/' + request_id, headers= headers)
        #request_id = response_status.json()['id']
        status = response_status.json()['status']
        if status == 'FINISHED':
            done = True
            log_processing(request_id, done, count)
        else:
            time.sleep(10)
            log_processing(request_id, done, count)
            count += 1


def downloader(start, running, finished, download_folder, request_id, token):
    '''
    This module downloads all requested data
    :return:
    '''
    # write data downloader

    headers = {
        'Origin': 'https://apps.sentinel-hub.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.9,sl;q=0.8',
        'Authorization': 'Bearer ' + token +'',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://apps.sentinel-hub.com/mosaic-hub/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Connection': 'keep-alive',
    }

    order_list = requests.get('https://services-s2gm.sentinel-hub.com/mosaic/index/v1/mosaic/', headers=headers).json()
    order_list_data = json.loads(order_list)[0]

    mosaic_id = '321'
    url=''
    start = True
    log_download(start, running, finished, url)
    running = True
    log_download(start, running, finished, url)
    tile_number = int(requests.get('https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/maxDownloadSequence', headers=headers).json())
    for count in range(1,tile_number+1):
        data_list = requests.get('https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/'+ mosaic_id +'/sequence/' + str(count) + '/metadata', headers=headers).json()
        for file in data_list['files']:
            url = 'https://services-s2gm.sentinel-hub.com/mosaic/download/v1/mosaic/' + mosaic_id + '/sequence/1?filename=' + file
            file_response = requests.get(url, headers=headers, stream=True)
            with open(download_folder + file, 'wb') as out_file:
                shutil.copyfileobj(file_response.raw, out_file)
            del file_response
            #log_download(start, running, finished, url)
            print(file)
    running = False
    finished = True
    log_download(start, running, finished, url)

def main(GRANULE_LIST, RANDOMIZE, START, RUNNING, FINISHED, DOWNLOAD_FOLDER):
    token, userid, request_id = make_request()
    check_processing_status(token, userid, request_id)
    downloader(START, RUNNING, FINISHED, DOWNLOAD_FOLDER, request_id, token)

if __name__ == '__main__':
    main(GRANULE_LIST, RANDOMIZE, START, RUNNING, FINISHED, DOWNLOAD_FOLDER)