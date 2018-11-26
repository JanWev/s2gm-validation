import glob, os
import pickle

# from ..utilities.static_parameters import DOWNLOAD_FOLDER
from validation_tools.utilities.static_parameters import DOWNLOAD_FOLDER as IMPORT_FOLDER

def import_all_static_parameter_variables():
    with open(IMPORT_FOLDER + 'variables/static_parameters_variables.pkl', 'rb') as f:
        DOWNLOAD_FOLDER = pickle.load(f)
        static_granule_list = pickle.load(f)
        static_granule_dict = pickle.load(f)
        random_granule_number = pickle.load(f)
        random_granule_list = pickle.load(f)
        random_granule_dict = pickle.load(f)
        static_granule_format = pickle.load(f)
        image_formats = pickle.load(f)
        resolution_list = pickle.load(f)
        static_resolution = pickle.load(f)
        coordinate_system_list = pickle.load(f)
        static_projection = pickle.load(f)
        basic_ref_band_list = pickle.load(f)
        ext_ref_band_list = pickle.load(f)
        aux_band_list = pickle.load(f)
        static_band = pickle.load(f)
        period_list = pickle.load(f)
        static_periods = pickle.load(f)
        static_dates = pickle.load(f)

    return DOWNLOAD_FOLDER, static_granule_list, static_granule_dict, \
    random_granule_number, random_granule_list, random_granule_dict, \
    static_granule_format, image_formats, resolution_list, static_resolution,\
    coordinate_system_list, static_projection, basic_ref_band_list, \
    ext_ref_band_list, aux_band_list, static_band, period_list, static_periods, \
    static_dates

def folder_names(IMPORT_FOLDER, name, resolution, period, date):

    basefolder = IMPORT_FOLDER + 'R' + date[0:4] + date[5:7] + date[8:10] + period[0] + str(resolution) + '_' + name + '_STD_v0.1.0_'

    return basefolder, subfolder

def check_file_format():


def completeness_test():
    # import all static_parameter_variables
    DOWNLOAD_FOLDER, static_granule_list, static_granule_dict, \
    random_granule_number, random_granule_list, random_granule_dict, \
    static_granule_format, image_formats, resolution_list, static_resolution, \
    coordinate_system_list, static_projection, basic_ref_band_list, \
    ext_ref_band_list, aux_band_list, static_band, period_list, static_periods, \
    static_dates = import_all_static_parameter_variables()

    #set number of products from request
    num_products = 4 + random_granule_number

    #import request variables
    os.chdir(IMPORT_FOLDER + 'variables/')
    request_variable_list = []
    for file in glob.glob('request_variables_*.pkl'):
        request_variable_list.append(file)

    #import request parameters
    with open(IMPORT_FOLDER + 'variables/request_parameters.pkl', 'rb') as f:
        request_parameters = pickle.load(f)
    for prod_id in range(1, num_products + 1):
        print(prod_id)
        if prod_id < 10:
            name = request_parameters[0]['0'+str(prod_id)]
            imageFormat = request_parameters[1]['0'+str(prod_id)]
            resolution = request_parameters[2]['0'+str(prod_id)]
            coordsys = request_parameters[3]['0'+str(prod_id)]
            bands = request_parameters[4]['0'+str(prod_id)]
            coordinates = request_parameters[5]['0'+str(prod_id)]
            period = request_parameters[6]['0'+str(prod_id)]
            date = request_parameters[7]['0'+str(prod_id)]
            # import request variables
            with open(IMPORT_FOLDER + 'variables/' + 'request_variables_0' + str(prod_id) + '.pkl', 'rb') as f:
                [request_id, order_name, start_date, end_date, temporal_period, resolution] = pickle.load(f)
        else:
            name = request_parameters[0][str(prod_id)]
            imageFormat = request_parameters[1][str(prod_id)]
            resolution = request_parameters[2][str(prod_id)]
            coordsys = request_parameters[3][str(prod_id)]
            bands = request_parameters[4][str(prod_id)]
            coordinates = request_parameters[5][str(prod_id)]
            period = request_parameters[6][str(prod_id)]
            date = request_parameters[7][str(prod_id)]
            with open(IMPORT_FOLDER + 'variables/' + 'request_variables_' + str(prod_id) + '.pkl', 'rb') as f:
                [request_id, order_name, start_date, end_date, temporal_period, resolution] = pickle.load(f)

        print(name + ', ' + imageFormat + ', ' + resolution + ', ' + coordsys + ', ' + bands + ', ' + coordinates + ', ' + period + ', ' + date + ', ' + request_id)



        basefolder, subfolder, = folder_names(IMPORT_FOLDER, name, resolution, period, date)

        check_file_format(name, resolution, period, date)


    for pkl_file_name in request_variable_list:
        with open(IMPORT_FOLDER + 'variables/' + pkl_file_name, 'rb') as f:
            print(f)

if __name__ == '__main__':
    completeness_test()