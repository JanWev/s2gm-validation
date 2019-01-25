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
            test_result['result'] = {
                'finished': False,
                'passed': False,
                'Error': 'Validation failed ResourceReportResource in JSON'
            }
        elif 'PullBatchReportResource' in json_data['value']:
            test_result['result'] = {
                'finished': False,
                'passed': False,
                'Error': 'Summary validation report of multiple resources not yet implemented'
            }
        else:
            test_result['result'] = {
                'finished': True,
                'passed': True
            }
    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': ex,
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
                if subdir.is_dir():
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
            # TODO: possibly check content within the nc file?
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

'''
Level 0 testing no. 3: Gets raster data from TIFF, JP2 or NC files within the defined validation folder. The following parameters are returned within the test_
result dictionary: file format,data type (for every band if more then one band is available), pixel size, nodata value, origin (only for TIFF and JP2)
'''
def level_0_3(test_metadata):

    test_result = {
        'test_id': 'level_0_3',
        'test_name': 'Raster inspection',
    }
    try:
        #go through directory and open all raster files (.jp2, .tiff, .nc)
        product_path = Path(test_metadata['validate_path'])
        for subdir in product_path.iterdir():
            path = str(product_path / subdir)
            if subdir.is_dir():
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
                            'image_path': file,
                        }
                        test_result['FILE: ' + file] = int_test_result
                    elif image_file.endswith('jp2') or image_file.endswith('tiff'):
                        img = gdal.Open(image_file)
                        info = gdal.Info(img, format='json')
                        gt = img.GetGeoTransform()
                        CellSize = (gt[1], gt[5])
                        origin = (gt[0], gt[3])
                        band = img.GetRasterBand(1)
                        nodata = band.GetNoDataValue()
                        datatype = info['bands'][0]['type']
                        file_format = info['driverShortName']

                        prj = img.GetProjection()
                        srs = osr.SpatialReference(wkt=prj)
                        if srs.IsProjected:
                            projection = (srs.GetAttrValue('projcs'))
                        else:
                            projection = (srs.GetAttrValue('geogcs'))
                        int_test_result = {
                            'File_format': file_format,
                            'Pixel_size': CellSize,
                            'NODATA_value': nodata,
                            'Data_type': datatype,
                            'Projection': projection,
                            'image_path': file,
                            'origin': origin
                        }
                        test_result['FILE: ' + file] = int_test_result

    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': ex,
        }
    return test_result


'''
Level 0 test no.4: compares if all necessary information are available in the JSON file
'''

def level_0_4(test_metadata):

    test_result = {
        'test_id': 'level_0_4',
        'test_name': 'Compare JSON with reference JSON file',
    }
    try:
        product_path = Path(test_metadata['validate_path'])
        #reference_path = Path(test_metadata['reference_path'])
        reference_path = ('T:/Processing/2721_S2GM/02_Interim_Products/mosaics/32TPT_20m_Day_S2B_new/S2GM_D20_20180713_20180713_32TPT_QAtest_S2B_20m_new_STD_v1.0.4_33888/32TPT_QAtest_S2B_20m_new/metadata_D20_20180713_32TPT_QAtest_S2B_20m_new.json')
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
                            value = json_reference[key]
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
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': ex,
        }
    return test_result

