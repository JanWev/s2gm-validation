# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Convert stored request metadata to json format.

Format example:
{
"bands": ["B02", "B03", "B04", "B8A", "B07", "B01", "INDEX", "SNOW"],
"tile_ids": "T30UVC",
"compositing_period": "DAY",
"mosaic_start_date": "2018-04-15",
"request_status": "processed",
"order_id": "258c39f1-8e3f-45fd-bb18-a1cbbdc40ef9",
"resolution": "R60m",
"image_format": "NETCDF",
"order_name": "S2GM_valreq_20190115T155053_rand04_T30UVC",
"projection": "WGS84",
"mosaic_end_date": "2018-04-15"
}
"""

import os
import pickle, json
from .static_download_parameters import static_granule_format, static_projection, static_band, static_granule_list

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def run(DOWNLOAD_FOLDER, prod_id):
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
                [request_id, order_name, start_date, end_date, temporal_period, resolution, order_number] = pickle.load(
                    f)

    prod_folders = os.listdir(path=DOWNLOAD_FOLDER)

    # convert static granules metadata
    if prod_id <= 4:
        dict_identifier = '0'+str(prod_id)
        data = {}
        if start_date == '':
            data['request_status'] = 'rejected'
        else:
            data['request_status'] = 'processed'
            data['bands'] = static_band[dict_identifier][10:-2].replace('",','').replace('"', '').split()
            data['order_name'] = order_name
            data['order_id'] = request_id
            data['mosaic_start_date'] = start_date.strftime('%Y-%m-%d')
            data['compositing_period'] = temporal_period
            data['image_format'] = static_granule_format[dict_identifier]
            data['resolution'] = resolution
            data['projection'] = static_projection[dict_identifier]
            data['tile_ids'] = static_granule_list[prod_id-1]
            data['mosaic_end_date'] = end_date.strftime('%Y-%m-%d')

            for entry in prod_folders:
                if entry.find(order_name) != -1:
                    prod_folder = entry
            with open(DOWNLOAD_FOLDER + prod_folder + '/validation.json', 'w') as outfile:
                json.dump(data, outfile)


    else:
        # convert random granules metadata
        random_counter = prod_id - 5
        dict_identifier = '0'+str(prod_id)
        data = {}
        if start_date == '':
            data['request_status'] = 'rejected'
        else:
            data['request_status'] = 'processed'
            band_file = DOWNLOAD_FOLDER + 'variables/bands.pkl'
            with open(band_file, 'rb') as f:
                bands = pickle.load(f)
            format_file = DOWNLOAD_FOLDER + 'variables/formats.pkl'
            with open(format_file, 'rb') as f:
                formats = pickle.load(f)
            proj_file = DOWNLOAD_FOLDER + 'variables/projections.pkl'
            with open(proj_file, 'rb') as f:
                projection = pickle.load(f)
            id_file = DOWNLOAD_FOLDER + 'variables/ids.pkl'
            with open(id_file, 'rb') as f:
                granule = pickle.load(f)
            data['bands'] = bands[random_counter][10:-2].replace('",',' ').replace('"', '').split()
            data['order_name'] = order_name
            data['order_id'] = request_id
            data['mosaic_start_date'] = start_date.strftime('%Y-%m-%d')
            data['compositing_period'] = temporal_period
            data['image_format'] = formats[random_counter]
            data['resolution'] = resolution
            data['projection'] = projection[random_counter]
            data['tile_ids'] = granule[random_counter]
            data['mosaic_end_date'] = end_date.strftime('%Y-%m-%d')
            for entry in prod_folders:
                if entry.find(order_name) != -1:
                    prod_folder = entry
            with open(DOWNLOAD_FOLDER + prod_folder + '/validation.json', 'w') as outfile:
                json.dump(data, outfile)

