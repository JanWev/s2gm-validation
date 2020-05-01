# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L0 tests.
"""

from validation_tools.utilities import validation_metadata
from pathlib import Path
import json
from urllib.request import urlopen, Request
from osgeo import gdal, osr
import os

__author__ = 'florian girtler - girtler@geoville.com, rafael reder - reder@geoville.com'

"""
Level 0 test no. 2: Checking the integrity of files
"""


def level_0_2(test_metadata):
    test_result = {
        'test_id': 'level_0_2',
        'test_name': 'Check integrity of files',
    }

    try:
        product_path = Path(test_metadata['validate_path'])
        inspire_file = str(product_path / 'inspire.xml')
        metadata = open(inspire_file).read()
        """validate metadata against INSPIRE metadata validation service"""
        host = 'http://inspire-geoportal.ec.europa.eu'
        endpoint = 'GeoportalProxyWebServices/resources/INSPIREResourceTester'
        url = '{}/{}'.format(host, endpoint)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'text/plain'
        }
        request = Request(url, data=metadata.encode("utf-8"), headers=headers)
        response = urlopen(request)

        json_data = json.loads(response.read().decode('utf-8'))

        if 'ResourceReportResource' in json_data['value']:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'Error': 'Validation failed ResourceReportResource in JSON'
            }
        elif 'PullBatchReportResource' in json_data['value']:
            test_result['status'] = {
                'finished': False,
                'passed': False,
                'Error': 'Summary validation report of multiple resources not yet implemented'
            }
        else:
            test_result['status'] = {
                'finished': True,
                'passed': True
            }

    except ConnectionResetError:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': 'INSPIRE validator service not available',
            }

    except Exception as ex:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }

    return test_result


"""
Level 0 test no. 1: Checking if all required files are there
"""


def level_0_1(test_metadata):

    test_result = {
        'test_id': 'level_0_1',
        'test_name': 'Check of completeness',
    }

    try:
        missing_files = []
        unexpected_files = []
        product_path = Path(test_metadata['validate_path'])

        # check if inspire conform xml file is available
        inspire_file = product_path / 'inspire.xml'
        if not inspire_file.is_file():
            missing_files.append(inspire_file)

        """
        distinguish between netcdf and others
            - when netcdf only one file is available -> possibly check within the file?
            - when not netcdf then a metadata json file should be available?
        """
        if not test_metadata['image_format'].lower() == 'netcdf':
            required_file_prefixes = validation_metadata.get_required_file_prefixes(test_metadata)

            # go through each subdirectory (tile) of the product and check if there are all required files
            for subdir in product_path.iterdir():
                # ignoring the subfolder if it is named 'val_res'
                if subdir.is_dir() and subdir.name != 'val_res':
                    found_required_prefixes = []
                    found_required_files = []

                    available_files = [x.name for x in subdir.iterdir() if not x.is_dir()]

                    # go through all required file prefixes and check if according files are available in the current subdir
                    for rf in required_file_prefixes:
                        for af in available_files:
                            if af.startswith(rf):
                                found_required_prefixes.append(rf)
                                found_required_files.append(af)

                    missing = set(required_file_prefixes) - set(found_required_prefixes)
                    for m in missing:
                        missing_files.append('{}/{}...'.format(subdir.name, m))

                    unexpected = set(available_files) - set(found_required_files)
                    for u in unexpected:
                        unexpected_files.append('{}/{}'.format(subdir.name, u))

        else:
            # check if netcdf file is available in each subdir (tile?)
            for subdir in product_path.iterdir():
                if subdir.is_dir():
                    found_netcdf_files = []

                    available_files = [x.name for x in subdir.iterdir() if not x.is_dir()]

                    # go through all available files and check netcdf files are available in the current subdir
                    for af in available_files:
                        if af.endswith('.nc'):
                            found_netcdf_files.append(af)

                    if len(found_netcdf_files) < 1:
                        missing_files.append('{}/...nc'.format(subdir.name))

                    unexpected = set(available_files) - set(found_netcdf_files)
                    for u in unexpected:
                        unexpected_files.append('{}/{}'.format(subdir.name, u))

        # fill test result
        test_passed = True
        if len(missing_files) > 0:
            test_passed = False
            test_result['missing_files'] = missing_files
        if len(unexpected_files) > 0:
            test_result['unexpected_files'] = unexpected_files

        test_result['status'] = {
            'finished': True,
            'passed': test_passed
        }

    except Exception as ex:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }

    return test_result

'''
Level 0 testing no. 3: Gets raster data from TIFF, JP2 or NC files within the defined validation folder. The following parameters are returned within the test_
result dictionary: file format,data type (for every band if more then one band is available), pixel size, nodata value, origin (only for TIFF and JP2). Compares
with validation JSON
'''
test_result = {
        'test_id': 'level_0_3',
        'test_name': 'Raster_inspection',
    }


def level_0_3(test_metadata):

    test_result = {
        'test_id': 'level_0_3',
        'test_name': 'Raster_inspection',
    }

    try:
        file_list = []
        product_path = Path(test_metadata['validate_path'])
        with open(str(Path(product_path / 'validation.json')), 'r') as validation_file:
            json_data = json.load(validation_file)
        for subdir in product_path.iterdir():
            path = str(product_path / subdir)
            if subdir.is_dir():
                file_list = []
                for file in os.listdir(path):
                    image_file = (path + '/' + file)
                    subdatasets_dict = {}
                    if image_file.endswith('nc'):
                        img = gdal.Open(image_file)
                        info = gdal.Info(img, format='json')
                        file_format = info['metadata']['']['netcdf_version']
                        pixel_size = info['metadata']['']['spatial_resolution']
                        subdatasets = info['metadata']['SUBDATASETS']
                        for key in subdatasets:
                            subdatasets_dict[key] = subdatasets[key]
                            i = 0
                            for keys in info['metadata']['']:
                                if keys.startswith('B') and i < 1:
                                    i = i + 1
                                    band = keys[0:3]
                                    nodatavalue = info['metadata']['']['%s__FillValue' % band]
                                    projection = info['metadata']['']['%s_coordinates' % band]
                        int_test_result = {
                            'subdatasets': subdatasets_dict,
                            'pixel_size': pixel_size,
                            'file_format': file_format,
                            'nodatavalue': nodatavalue,
                            'projection': projection,
                        }
                        for element in subdatasets_dict:
                            file_list.append(subdatasets_dict[element])
                        test_result['FILE: ' + file] = int_test_result
                        file_list.append(file)
                        if projection == 'lat lon' and json_data['projection'] == 'WGS84':
                            test_result['coordinate_system_correct'] = True
                            test_result['test_passed'] = True
                        else:
                            test_result['coordinate_system_correct'] = False
                            test_result['test_passed'] = False
                        if pixel_size == json_data['resolution'][1:]:
                            test_result['resolution as ordered'] = True
                            test_result['test_passed'] = True
                        else:
                            test_result['resolution as ordered'] = False
                            test_result['test_passed'] = False

                    elif image_file.endswith('jp2') or image_file.endswith('tiff'):
                        img = gdal.Open(image_file)
                        info = gdal.Info(img, format='json')
                        gt = img.GetGeoTransform()
                        pixel_size = (gt[1], gt[5])
                        origin = (gt[0], gt[3])
                        band = img.GetRasterBand(1)
                        nodata = band.GetNoDataValue()
                        datatype = info['bands'][0]['type']
                        file_format = info['driverShortName']
                        prj = img.GetProjection()
                        srs = osr.SpatialReference(wkt=prj)
                        if srs.GetAttrValue('projcs') is None:
                            projection = srs.GetAttrValue('geogcs')
                        else:
                            projection = srs.GetAttrValue('projcs')
                        int_test_result = {
                            'File_format': file_format,
                            'Pixel_size': pixel_size,
                            'NODATA_value': nodata,
                            'Data_type': datatype,
                            'Projection': projection,
                            'origin': origin
                        }
                        test_result['FILE: ' + file] = int_test_result
                        file_list.append(file)
                        if projection[9:12] == 'UTM' and json_data['projection'] == 'UTM':
                            test_result['coordinate_system_correct'] = True
                            test_result['test_passed'] = False
                        elif projection == 'WGS 84' and json_data['projection'] == 'WGS84':
                            test_result['coordinate_system_correct'] = True
                            test_result['test_passed'] = True
                        else:
                            test_result['coordinate_system_correct'] = False
                            test_result['test_passed'] = False
                        if int(pixel_size[0]) == int(json_data['resolution'][1:3]):
                            test_result['resolution as ordered'] = True
                            test_result['test_passed'] = True
                        else:
                            test_result['resolution as ordered'] = False
                            test_result['test_passed'] = False
                    else:
                        pass

        band_list = []
        for ord_band in json_data['bands']:
            for av_band in file_list:
                if ord_band in av_band or ord_band.lower() in av_band:
                    band_list.append(av_band)
        if len(band_list) == len(json_data['bands']):
            test_result['Ordered bands/subdatasets present:'] = True
            test_result['test_passed'] = True
        elif len(band_list)/2 == len(json_data['bands']):
            test_result['Ordered bands/subdatasets present:'] = True
            test_result['test_passed'] = True
        else:
            if not file_list:
                test_result['error'] = 'No image files in folder available'
                test_result['test_passed'] = False
            else:
                test_result['Ordered bands/subdatasets present:'] = False
                test_result['test_passed'] = False
        test_result['finished'] = True

    except Exception as ex:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }
    return test_result


'''
Level 0 test no.4: tests completeness of the JSON file
'''


def level_0_4(test_metadata):

    test_result = {
        'test_id': 'level_0_4',
        'test_name': 'Compare JSON with reference JSON file',
    }
    try:
        product_path = Path(test_metadata['validate_path'])
        reference_path = Path(test_metadata['reference_path'])
        for subdir in product_path.iterdir():
            path = str(product_path / subdir)
            if subdir.is_dir():
                for file in os.listdir(path):
                    val_file_path = (path + '/' + file)
                    if file.endswith('json'):
                        test_result['file_name'] = file
                        validation_file = open(val_file_path)
                        reference_file = open(str(reference_path))
                        json_reference = json.load(reference_file)
                        json_validation = json.load(validation_file)

                        missing_keys = []

                        for key in json_reference.keys():
                            if key not in json_validation:
                                missing_keys.append(key)

                        if not missing_keys:
                            test_result['Check with reference JSON passed:'] = True
                        else:
                            test_result['DIFFERENCE from reference JSON'] = missing_keys
                    else:
                        pass
        json_av = 'Check with reference JSON passed:'
        if json_av not in test_result:
            test_result['Error:'] = 'No JSON available'

    except Exception as ex:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }
    return test_result
