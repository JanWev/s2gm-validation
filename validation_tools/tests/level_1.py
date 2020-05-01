from osgeo import gdal
from pathlib import Path
import os
import inspect


"""
Level 1 test no. 0: Creates RGB jpg (JPEG) or png (NETCDF, TIFF) for visual inspection and vrt stack (JPEG, TIFF)
"""
def level_1_0(test_metadata, val_res_path):


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
                    if file.endswith('nc'):
                        tag = 'ns'
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
                        if tag == 'jp2':
                            if len(rgb_list) == 3 and i == 0:
                                gdal.BuildVRT(destName=str(val_res_path) + '/temp.vrt', srcDSOrSrcDSTab=rgb_list,
                                              options=gdal.BuildVRTOptions(separate=True, srcNodata=nodata))
                                gdal.Translate(destName=str(val_res_path) + '/' + tile + '_RGB.tif',
                                               srcDS=str(val_res_path) + '/temp.vrt',
                                               options=gdal.TranslateOptions(noData=nodata))
                                gdal.Translate(destName=str(val_res_path) + '/' + tile + '_RGB.jpg',
                                               srcDS=str(val_res_path) + '/' + tile + '_RGB.tif',
                                               options=gdal.TranslateOptions(format='JPEG', scaleParams=[[0, 1400]]))
                                os.remove(str(val_res_path) + '/temp.vrt')
                                os.remove(str(val_res_path) + '/' + tile + '_RGB.tif')
                                print('RGB for {} created'.format(tile))
                                i = 1

                if tag == 'tif' or tag =='jp2':
                    if 'B08' in file_dict and 'B8A' in file_dict:
                        del file_dict['B8A']
                    file_list = []
                    for element in file_dict.values():
                        file_list.append(element)
                    gdal.BuildVRT(destName=str(val_res_path) + '/' + tile + '_vrt_stack.vrt', srcDSOrSrcDSTab=file_list,
                                  options=gdal.BuildVRTOptions(separate=True, srcNodata=nodata))

                    for file in os.listdir(path):
                        if file.endswith('json') and file != 'validation_report.json':
                            tag = 'json'
                            current_path, dir = os.path.split(os.path.dirname(__file__))
                            print(current_path)
                            cmd = 'pconvert -f png -H 550 -p "' + current_path + '\\aux_data\\s2Profile_B432.rgb" -o ' + val_res_path + ' ' + str(
                                subdir) + '\\' + file
                            print(cmd)
                            prods_path, prod_name = os.path.split(str(product_path))
                            prod_path, new_prod_name = os.path.split(str(path))

                    if len(rgb_list) == 3 and i == 0 and tag == 'json':
                        os.system(cmd)
                        for element in os.listdir(val_res_path):
                            if element.startswith(prod_name[:7]):
                                os.rename(val_res_path + '/' + element,
                                          val_res_path + '/' + new_prod_name + '.png')
                        # os.rename(val_res_path + '/' + prod_name + '.png', val_res_path + '/' + new_prod_name + '.png')
                        i = 1

                if tag == 'ns':
                    current_path, dir = os.path.split(os.path.dirname(__file__))
                    print(current_path)
                    cmd = 'pconvert -f png -H 550 -p "' + current_path + '\\aux_data\\s2Profile_B432.rgb" -o ' + val_res_path + ' ' + str(
                        subdir) + '\\' + file
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

                        prods_path, prod_name = os.path.split(str(product_path))
                        prod_path, new_prod_name = os.path.split(str(path))

                        for element in os.listdir(val_res_path):
                            if element.startswith(prod_name[5:16]):
                                os.rename(val_res_path + '/' + element,
                                          val_res_path + '/' + new_prod_name + '.png')



                    else:
                        test_result['status'] = {
                            'finished': False,
                            'passed': False,
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

            test_result['status'] = {
                'finished': True,
                'passed': True,
            }


    except Exception as ex:
        test_result['status'] = {
            'finished': False,
            'passed': False,
            'error': str(ex),
        }

    return test_result
