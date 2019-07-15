from osgeo import gdal
from pathlib import Path
import os
import inspect


"""
Level 1 test no. 0: Creates RGB tiff and jpg for visual inspection
"""
def level_1_0(test_metadata):


    test_result = {
        'test_id': 'level_1_0',
        'test_name': 'RGB quicklook and vrt stack',
    }

    try:
        product_path = Path(test_metadata['validate_path'])
        for subdir in product_path.iterdir():
            path = str(product_path / subdir)
            if subdir.is_dir():
                tile = os.path.basename(os.path.normpath(str(subdir)))
                rgb_list = []
                file_dict = {}
                tag = ''
                i = 0
                for file in os.listdir(path):
                    if file.endswith('tiff'):
                        tag = 'tif'
                    if file.endswith('jp2'):
                        tag = 'jp2'
                    if file.endswith('tiff') or file.endswith('jp2'):
                        if file.startswith('B'):
                            file_dict[file[0:3]] = path + '/' + file
                            try:
                                blue_band = file_dict['B02']
                                green_band = file_dict['B03']
                                red_band = file_dict['B04']
                                img = gdal.Open(blue_band)
                                band = img.GetRasterBand(1)
                                nodata = band.GetNoDataValue()
                                rgb_list = [red_band, green_band, blue_band]
                            except:
                                pass
                        if len(rgb_list) == 3 and i == 0:
                            gdal.BuildVRT(destName=str(product_path) + '/temp.vrt', srcDSOrSrcDSTab=rgb_list,
                                          options=gdal.BuildVRTOptions(separate=True, srcNodata=nodata))
                            gdal.Translate(destName=str(product_path) + '/' + tile + '_RGB.tif',
                                           srcDS=str(product_path) + '/temp.vrt',
                                           options=gdal.TranslateOptions(noData=nodata))
                            gdal.Translate(destName=str(product_path) + '/' + tile + '_RGB.jpg',
                                           srcDS=str(product_path) + '/' + tile + '_RGB.tif',
                                           options=gdal.TranslateOptions(format='JPEG', scaleParams=[[0, 1400]]))
                            os.remove(str(product_path) + '/temp.vrt')
                            print('RGB for {} created'.format(tile))
                            i = 1
                if tag == 'tif':
                    if 'B08' in file_dict and 'B8A' in file_dict:
                        del file_dict['B8A']
                    file_list = []
                    for element in file_dict.values():
                        file_list.append(element)
                    gdal.BuildVRT(destName=str(product_path) + '/vrt_stack.vrt', srcDSOrSrcDSTab=file_list,
                                  options=gdal.BuildVRTOptions(separate=True, srcNodata=nodata))

                for file in os.listdir(path):
                    if file.endswith('.nc'):
                        tag = 'ns'
                        img = gdal.Open(path + '/' + file)
                        info = gdal.Info(img, format='json')
                        nodatavalue = info['metadata']['']['B02__FillValue'][0:-2]
                        subdatasets = img.GetSubDatasets()
                        for variable in subdatasets:
                            if variable[0].endswith('lat'):
                                lat = variable[0]
                                lat = lat.replace('\\', '/')
                                info = gdal.Info(lat, format='json')
                                lat_max = info['metadata']['']['geospatial_lat_max']
                                lat_min = info['metadata']['']['geospatial_lat_min']
                                lon_max = info['metadata']['']['geospatial_lon_max']
                                lon_min = info['metadata']['']['geospatial_lon_min']
                        for variable in subdatasets:
                            if variable[0].endswith('B02'):
                                blue_band = variable[0]
                                blue_band = blue_band.replace('\\', '/')
                                rgb_list.append(blue_band)

                            if variable[0].endswith('B03'):
                                green_band = variable[0]
                                green_band = green_band.replace('\\', '/')
                                rgb_list.insert(0, green_band)

                            if variable[0].endswith('B04'):
                                red_band = variable[0]
                                red_band = red_band.replace('\\', '/')
                                rgb_list.insert(0, red_band)

                        if len(rgb_list) == 3:
                            gdal.Translate(destName=path + '/blue.tif', srcDS=blue_band,
                                           options=gdal.TranslateOptions(noData=nodatavalue, format='GTIFF',
                                                                         outputBounds=[lon_min, lat_max, lon_max,
                                                                                       lat_min],
                                                                         scaleParams=[[0, 1500]]))
                            gdal.Translate(destName=path + '/green.tif', srcDS=green_band,
                                           options=gdal.TranslateOptions(noData=nodatavalue, format='GTIFF',
                                                                         outputBounds=[lon_min, lat_max, lon_max,
                                                                                       lat_min],
                                                                         scaleParams=[[0, 1500]]))
                            gdal.Translate(destName=path + '/red.tif', srcDS=red_band,
                                           options=gdal.TranslateOptions(noData=nodatavalue, format='GTIFF',
                                                                         outputBounds=[lon_min, lat_max, lon_max,
                                                                                       lat_min],
                                                                         scaleParams=[[0, 1500]]))
                            gdal.BuildVRT(destName=path + '/temp.vrt', srcDSOrSrcDSTab=rgb_list,
                                          options=gdal.BuildVRTOptions(separate=True, srcNodata=nodatavalue))
                            gdal.Translate(destName=path + '/RGB.tif', srcDS=path + '/temp.vrt',
                                           options=gdal.TranslateOptions(noData=nodatavalue,
                                                                         outputBounds=[lon_min, lat_max, lon_max,
                                                                                       lat_min],
                                                                         scaleParams=[[0, 1500]]))
                            gdal.Translate(destName=path + '/RGB.jpg', srcDS=path + '/RGB.tif',
                                           options=gdal.TranslateOptions(format='JPEG', noData=nodatavalue,
                                                                         scaleParams=[[0, 1500]]))
                        else:
                            test_result['result'] = {
                                'finished': False,
                                'error': 'Not all required bands for RGB available (missing bands)'
                            }
                            continue

            try:
                for element in os.listdir(path):
                    if element.startswith('blue') or element.startswith('red') or element.startswith('green') or \
                            element.startswith('temp'):
                        os.remove(path + '/' + element)
            except:
                pass

            test_result['result'] = {
                'finished': True,
            }


    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }

    print('Level 1 check done!')
    return test_result

def level_1_1(test_metadata, val_res_path):


    test_result = {
        'test_id': 'level_1_1',
        'test_name': 'RGB quicklook',
    }

    try:
        product_path = Path(test_metadata['validate_path'])
        for subdir in product_path.iterdir():
            path = str(product_path / subdir)
            if subdir.is_dir():
                tile = os.path.basename(os.path.normpath(str(subdir)))
                rgb_list = []
                file_dict = {}
                tag = ''
                i = 0
                for file in os.listdir(path):
                    if file.endswith('json'):
                        tag = 'json'
                        current_path, dir = os.path.split(os.path.dirname(__file__))
                        print(current_path)
                        cmd = 'pconvert -f png -H 550 -p "' + current_path + '\\aux_data\\s2Profile_B432.rgb" -o ' + val_res_path + ' ' + str(
                            subdir) + '\\' + file
                        print(cmd)
                        prods_path, prod_name_temp = os.path.split(str(product_path))
                        prod_name = prod_name_temp.rsplit('_', 1)[0]
                    if file.endswith('tiff') or file.endswith('jp2'):
                        if file.startswith('B'):
                            file_dict[file[0:3]] = path + '/' + file
                            prod_path, new_prod_name = os.path.split(str(path))
                            try:
                                blue_band = file_dict['B02']
                                green_band = file_dict['B03']
                                red_band = file_dict['B04']
                                rgb_list = [red_band, green_band, blue_band]
                            except:
                                pass
                if len(rgb_list) == 3 and i == 0 and tag == 'json':
                    os.system(cmd)
                    # for element in os.listdir(val_res_path):
                    #     if element.startswith(prod_name[:-7]):
                    #         os.rename(val_res_path + '/' + element,
                    #                   val_res_path + '/' + new_prod_name + '.png')
                    # os.rename(val_res_path + '/' + prod_name + '.png', val_res_path + '/' + new_prod_name + '.png')
                    i = 1

                for file in os.listdir(path):
                    if file.endswith('.nc'):
                        current_path, dir = os.path.split(os.path.dirname(__file__))
                        print(current_path)
                        cmd = 'pconvert -f png -H 550 -p "' + current_path + '\\aux_data\\s2Profile_B432.rgb" -o ' + val_res_path + ' ' + str(subdir) + '\\' + file
                        print(cmd)
                        img = gdal.Open(path + '/' + file)
                        subdatasets = img.GetSubDatasets()
                        for variable in subdatasets:
                            if variable[0].endswith('B02'):
                                blue_band = variable[0]
                                blue_band = blue_band.replace('\\', '/')
                                rgb_list.append(blue_band)

                            if variable[0].endswith('B03'):
                                green_band = variable[0]
                                green_band = green_band.replace('\\', '/')
                                rgb_list.insert(0, green_band)

                            if variable[0].endswith('B04'):
                                red_band = variable[0]
                                red_band = red_band.replace('\\', '/')
                                rgb_list.insert(0, red_band)

                        if len(rgb_list) == 3:
                            os.system(cmd)

                        else:
                            test_result['result'] = {
                                'finished': False,
                                'error': 'Not all required bands for RGB available (missing bands)'
                            }
                            continue

            test_result['result'] = {
                'finished': True,
            }


    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }

    print('Level 1 check done!')
    return test_result
