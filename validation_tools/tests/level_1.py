from osgeo import gdal
from pathlib import Path
import os


"""
Level 1 test no. 0: Creates RGB for visual inspection
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
                file_list = []
                i = 0
                for file in os.listdir(path):
                    if file.endswith('tiff'):
                        file_list.append(path + '/' + file)
                        if file.startswith('B02'):
                            blue_band = path + '/' + file
                            img = gdal.Open(blue_band)
                            band = img.GetRasterBand(1)
                            nodata = band.GetNoDataValue()
                            rgb_list.insert(0, blue_band)
                        if file.startswith('B03'):
                            green_band = path + '/' + file
                            rgb_list.insert(0, green_band)
                        if file.startswith('B04'):
                            red_band = path + '/' + file
                            rgb_list.insert(0, red_band)
                        if len(rgb_list) == 3 and i == 0:
                            gdal.BuildVRT(destName=str(product_path) + '/temp.vrt', srcDSOrSrcDSTab=rgb_list,
                                          options=gdal.BuildVRTOptions(separate=True, srcNodata=nodata))
                            gdal.Translate(destName=str(product_path) + '/' + tile + '_RGB.tif',
                                           srcDS=str(product_path) + '/temp.vrt',
                                           options=gdal.TranslateOptions(noData=nodata))
                            os.remove(str(product_path) + '/temp.vrt')
                            i = 1

                gdal.BuildVRT(destName=str(product_path) + '/' + tile + '_stack.vrt', srcDSOrSrcDSTab=file_list,
                              options=gdal.BuildVRTOptions(separate=True, srcNodata=nodata,
                                                           allowProjectionDifference=True))
                for file in os.listdir(path):
                    if file.endswith('.nc'):
                        img = gdal.Open(path + '/' + file)
                        print(file)
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
                                gdal.Translate(destName=path + '/blue.tif', srcDS=blue_band,
                                               options=gdal.TranslateOptions(noData=65535, format='GTIFF',
                                                                             outputBounds=[lon_min, lat_max, lon_max,
                                                                                           lat_min]))
                            if variable[0].endswith('B03'):
                                green_band = variable[0]
                                green_band = green_band.replace('\\', '/')
                                rgb_list.insert(0, green_band)
                                gdal.Translate(destName=path + '/green.tif', srcDS=green_band,
                                               options=gdal.TranslateOptions(noData=65535, format='GTIFF',
                                                                             outputBounds=[lon_min, lat_max, lon_max,
                                                                                           lat_min]))
                            if variable[0].endswith('B04'):
                                red_band = variable[0]
                                red_band = red_band.replace('\\', '/')
                                rgb_list.insert(0, red_band)
                                gdal.Translate(destName=path + '/red.tif', srcDS=red_band,
                                               options=gdal.TranslateOptions(noData=65535, format='GTIFF',
                                                                             outputBounds=[lon_min, lat_max, lon_max,
                                                                                           lat_min]))

                gdal.BuildVRT(destName=path + '/temp.vrt', srcDSOrSrcDSTab=rgb_list,
                              options=gdal.BuildVRTOptions(separate=True, srcNodata=65535))
                gdal.Translate(destName=path + '/RGB.tif', srcDS=path + '/temp.vrt',
                               options=gdal.TranslateOptions(noData=65535,
                                                             outputBounds=[lon_min, lat_max, lon_max, lat_min]))
                try:
                    os.remove(path + '/' + 'temp.vrt')
                    os.remove(path + '/green.tif')
                    os.remove(path + '/red.tif')
                    os.remove(path + '/blue.tif')
                except:
                    pass

                test_result['result'] = {
                    'finished': True
                }

    except Exception as ex:
        test_result['result'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }

    return test_result