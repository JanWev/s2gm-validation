# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Convert stored request metadata to json format.
"""

import pickle
from .static_parameters import DOWNLOAD_FOLDER
from .static_parameters import static_granule_format, static_resolution, static_projection, static_band, \
    static_periods, static_dates

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def run(DOWNLOAD_FOLDER, prod_id):
    if prod_id <= 4:
        dict_identifier = '0'+str(prod_id)
        data = {}
        data['bands'] = static_band[dict_identifier][10:-2].replace('",','').replace('"', '').split()
        data['mosaic_start_date'] = static_dates[dict_identifier][0:-9]

        # convert static granules
    else:
        # convert random granules
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

        band_file = "K:/S2GM/S2GM_mosaics/v1.0.4/Python_downloads/0110_1404/variables/bands.pkl"

        with open(band_file, 'rb') as f:
            size = len(pickle.load(f))
            print(size)