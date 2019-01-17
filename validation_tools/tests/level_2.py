# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L2 tests. L2 checks for similarity of products
"""


import gdal

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def level_2_1(test_metadata, comparable):
    """
    Level 2 test no. 1: Spatial difference of SR for all bands
    """
    print(test_metadata)

    test_result = {
        'test_id': 'level_2_1',
        'test_name': 'Spatial difference of SR for all bands',
    }

    try:
        # TODO: do test
        if test_metadata['image_format'] == 'NETCDF':
            # TODO: implement xarray analysis
            driver_name = ''
        elif test_metadata['image_format'] == 'GEO_TIFF':
            driver_name = 'GTiff'
        else:
            driver_name = 'JP2OpenJPEG'
        driver = gdal.GetDriverByName('GTiff')
        driver.Register()
        # inData = gdal.Open(inFn)
        # raster = inData.GetRasterBand(1)
        # rasterAr = raster.ReadAsArray()
        # rasterAr[rasterAr == nodata] = 0
        # outraster = inData.GetRasterBand(1)
        # outrasterAr = outraster.ReadAsArray().astype(np.float)
        # outrasterAr[outrasterAr == nodata] = 0
        # inWkt, GeoT, rows, cols, Projection, pixelRes = GetGeoInfo(inData)

        # fill test result
        test_passed = True
        # TODO: check if test was passed

        test_result['result'] = {
            'finished': True,
            'passed': test_passed
        }

    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': ex,
        }

    return test_result