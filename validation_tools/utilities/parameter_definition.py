from datetime import datetime
from dateutil.relativedelta import relativedelta
import random
import pickle
import time
import os
from .static_download_parameters import DOWNLOAD_FOLDER, static_granule_list, static_granule_dict, \
    random_granule_number, random_granule_list, random_granule_dict, \
    static_granule_format, image_formats, resolution_list, static_resolution,\
    coordinate_system_list, static_projection, basic_ref_band_list, \
    ext_ref_band_list, aux_band_list, static_band, period_list, static_periods, \
    static_dates

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

RANDOMIZE = False  # This can be set to True if you like to create a new set of random Granules


def granule_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, random_granule_list):
    if randomize:
        random_ids = random.sample(random_granule_list, random_granule_number)
        with open(DOWNLOAD_FOLDER + 'variables/ids.pkl', 'wb') as f:
            pickle.dump(random_ids, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/ids.pkl', 'rb') as f:
                random_ids = pickle.load(f)
        except FileNotFoundError:
            print('IDs do not exist, start randomizing')
            random_ids = random.sample(random_granule_list, random_granule_number)
            with open(DOWNLOAD_FOLDER + 'variables/ids.pkl', 'wb') as f:
                pickle.dump(random_ids, f)

    return random_ids

def define_names(static_granule_list, random_granule_number, random_ids):
    names = {}
    for i in range(len(static_granule_list)):
        names.update({'0' + str(i + 1): 'S2GM_valreq_'
                         + str(datetime.now().strftime("%Y%m%dT%H%M%S")) +
                         '_stat0' + str(i + 1) + '_' +
                         str(static_granule_list[i])})

    for k in range(random_granule_number):
        if k  < 9:
            if k + len(static_granule_list) < 9:
                names.update({'0' + str(k + len(static_granule_list) + 1): 'S2GM_valreq_' + str(datetime.now().strftime("%Y%m%dT%H%M%S")) + '_rand0' + str(k + 1) + '_' + str(random_ids[k])})
            else:
                names.update({str(k + len(static_granule_list) + 1): 'S2GM_valreq_' + str(
                    datetime.now().strftime("%Y%m%dT%H%M%S")) + '_rand0' + str(k + 1) + '_' + str(random_ids[k])})

        else:
            names.update({str(k + len(static_granule_list) + 1): 'S2GM_valreq_' + str(datetime.now().strftime("%Y%m%dT%H%M%S")) + '_rand' + str(k + 1) + '_' + str(random_ids[k])})

    return names


def format_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number,
                      image_formats):
    if randomize:
        format_list = ['']*random_granule_number
        for i in range(random_granule_number):
            format_list[i] = (random.sample(image_formats, 1))[0]
        with open(DOWNLOAD_FOLDER + 'variables/formats.pkl', 'wb') as f:
            pickle.dump(format_list, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/formats.pkl', 'rb') as f:
                format_list = pickle.load(f)
        except FileNotFoundError:
            print('Formats do not exist, start randomizing')
            format_list = [''] * random_granule_number
            for i in range(random_granule_number):
                format_list[i] = (random.sample(image_formats, 1))[0]
            with open(DOWNLOAD_FOLDER + 'variables/formats.pkl', 'wb') as f:
                pickle.dump(format_list, f)

    return format_list

def define_format(DOWNLOAD_FOLDER, randomize, static_granule_format, random_granule_number,
                      image_formats):
    random_granule_format = format_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number,
                      image_formats)
    formats = {}
    formats.update(static_granule_format)
    for k in range(random_granule_number):
        if k + len(static_granule_format) + 1 < 10:
            formats.update({'0' + str(k + len(static_granule_format) + 1): random_granule_format[k]})
        else:
            formats.update({str(k + len(static_granule_format) + 1):
                                random_granule_format[k]})
    return formats


def resolution_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, resolution_list):
    if randomize:
        random_resolution_list = [''] * random_granule_number
        for i in range(random_granule_number):
            random_resolution_list[i] = (random.sample(resolution_list, 1))[0]
        with open(DOWNLOAD_FOLDER + 'variables/resolutions.pkl', 'wb') as f:
            pickle.dump(random_resolution_list, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/resolutions.pkl', 'rb') as f:
                random_resolution_list = pickle.load(f)
        except FileNotFoundError:
            print('Resolutions do not exist, start randomizing')
            random_resolution_list = [''] * random_granule_number
            for i in range(random_granule_number):
                random_resolution_list[i] = (random.sample(resolution_list, 1))[0]
            with open(DOWNLOAD_FOLDER + 'variables/resolutions.pkl', 'wb') as f:
                pickle.dump(random_resolution_list, f)

    return random_resolution_list


def define_resolutions(DOWNLOAD_FOLDER, randomize, random_granule_number, resolution_list,
                       static_resolution):
    random_granule_resolution = resolution_randomizer(DOWNLOAD_FOLDER, randomize,
                                                      random_granule_number,
                                                      resolution_list)
    resolutions = {}
    resolutions.update(static_resolution)
    for k in range(random_granule_number):
        if k + len(static_resolution) + 1 < 10:
            resolutions.update({'0' + str(k + len(static_resolution) + 1): random_granule_resolution[k]})
        else:
            resolutions.update({str(k + len(static_resolution) + 1):
                                    random_granule_resolution[k]})
    return resolutions


def projection_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, coordinate_system_list):
    if randomize:
        random_projection_list = [''] * random_granule_number
        for i in range(random_granule_number):
            random_projection_list[i] = (random.sample(coordinate_system_list, 1))[0]
        with open(DOWNLOAD_FOLDER + 'variables/projections.pkl', 'wb') as f:
            pickle.dump(random_projection_list, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/projections.pkl', 'rb') as f:
                random_projection_list = pickle.load(f)
        except FileNotFoundError:
            print('Projections do not exist, start randomizing')
            random_projection_list = [''] * random_granule_number
            for i in range(random_granule_number):
                random_projection_list[i] = (random.sample(coordinate_system_list, 1))[0]
            with open(DOWNLOAD_FOLDER + 'variables/projections.pkl', 'wb') as f:
                pickle.dump(random_projection_list, f)

    return random_projection_list


def define_projections(DOWNLOAD_FOLDER, randomize, random_granule_number, coordinate_system_list,
                       static_projection):
    random_granule_projection = projection_randomizer(DOWNLOAD_FOLDER, randomize,
                                                      random_granule_number,
                                                      coordinate_system_list)
    projections = {}
    projections.update(static_projection)
    for k in range(random_granule_number):
        if k + len(static_projection) + 1 < 10:
            projections.update({'0' + str(k + len(static_projection) + 1):
                                    random_granule_projection[k]})
        else:
            projections.update({str(k + len(static_projection) + 1):
                                    random_granule_projection[k]})
    return projections


def band_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, basic_ref_band_list,
                    ext_ref_band_list, aux_band_list):
    if randomize:
        random_band_list = [''] * random_granule_number
        complete_random_number = random_granule_number//5 #20%
        less_random_number = random_granule_number//5
        least_random_number = random_granule_number - (complete_random_number + less_random_number)

        for i in range(complete_random_number):
            num_bands = random.randrange(1, 22, 1)
            temp_band_list = random.sample(basic_ref_band_list + ext_ref_band_list + aux_band_list, num_bands)
            for k in range(len(temp_band_list)):
                if k == 0:
                    band_str = '{"bands":[' + temp_band_list[k]
                elif (k >0 and k < len(temp_band_list)-1 and len(temp_band_list)>2):
                    band_str += ',' + temp_band_list[k]
                else:
                    band_str += ',' + temp_band_list[k] + ']}'

            random_band_list[i] = band_str

        for i in range(less_random_number):
            num_bands = random.randrange(2, 22, 1)
            num_aux_bands = num_bands//2
            num_basic_bands = num_bands-num_aux_bands
            temp_basic_band_list = random.sample(basic_ref_band_list + ext_ref_band_list, num_basic_bands)
            temp_aux_band_list = random.sample(aux_band_list, num_aux_bands)
            for k in range(len(temp_basic_band_list + temp_aux_band_list)):
                if k == 0:
                    band_str = '{"bands":[' + (temp_basic_band_list + temp_aux_band_list)[k]
                elif (k >0 and k < len(temp_basic_band_list + temp_aux_band_list)-1):
                    band_str += ',' + (temp_basic_band_list + temp_aux_band_list)[k]
                else:
                    band_str += ',' + (temp_basic_band_list + temp_aux_band_list)[k] + ']}'
            random_band_list[complete_random_number+i] = band_str

        for i in range(least_random_number):
            num_bands = random.randrange(1, 19, 1)
            if num_bands//2 > len(ext_ref_band_list):
                num_ext_bands = len(ext_ref_band_list)
                num_aux_bands = num_bands - num_ext_bands
            else:
                num_aux_bands = num_bands//2
                num_ext_bands = num_bands-num_aux_bands
            if num_basic_bands > 8:
                num_refl_bands = 8
            else:
                num_refl_bands = num_basic_bands
            temp_ext_band_list = random.sample(ext_ref_band_list, num_refl_bands)
            temp_aux_band_list = random.sample(aux_band_list, num_aux_bands)
            temp_complete_band_list =  basic_ref_band_list + temp_ext_band_list + temp_aux_band_list
            for k in range(len(temp_complete_band_list)):
                if k == 0:
                    band_str = '{"bands":[' + (temp_complete_band_list)[k]
                elif (k >0 and k < len(temp_complete_band_list)-1):
                    band_str += ',' + (temp_complete_band_list)[k]
                else:
                    band_str += ',' + (temp_complete_band_list)[k] + ']}'
            random_band_list[complete_random_number + less_random_number + i] = band_str
        with open(DOWNLOAD_FOLDER + 'variables/bands.pkl', 'wb') as f:
            pickle.dump(random_band_list, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/bands.pkl', 'rb') as f:
                random_band_list = pickle.load(f)
        except FileNotFoundError:
            print('bands do not exist, start randomizing')
            random_band_list = [''] * random_granule_number
            complete_random_number = random_granule_number // 5  # 20%
            less_random_number = random_granule_number // 5
            least_random_number = random_granule_number - (
            complete_random_number + less_random_number)

            for i in range(complete_random_number):
                num_bands = random.randrange(1, 22, 1)
                temp_band_list = random.sample(
                    basic_ref_band_list + ext_ref_band_list + aux_band_list,
                    num_bands)
                for k in range(len(temp_band_list)):
                    if k == 0:
                        band_str = '{"bands":[' + temp_band_list[k]
                    elif (k > 0 and k < len(temp_band_list) - 1):
                        band_str += ',' + temp_band_list[k]
                    else:
                        band_str += ',' + temp_band_list[k] + ']}'

                random_band_list[i] = band_str

            for i in range(less_random_number):
                num_bands = random.randrange(2, 22, 1)
                num_aux_bands = num_bands // 2
                num_basic_bands = num_bands - num_aux_bands
                temp_basic_band_list = random.sample(
                    basic_ref_band_list + ext_ref_band_list, num_basic_bands)
                temp_aux_band_list = random.sample(aux_band_list,
                                                   num_aux_bands)
                for k in range(len(temp_basic_band_list + temp_aux_band_list)):
                    if k == 0:
                        band_str = '{"bands":[' + \
                                   (temp_basic_band_list + temp_aux_band_list)[
                                       k]
                    elif (k > 0 and k < len(
                                temp_basic_band_list + temp_aux_band_list) - 1):
                        band_str += ',' + (
                        temp_basic_band_list + temp_aux_band_list)[k]
                    else:
                        band_str += ',' + (
                        temp_basic_band_list + temp_aux_band_list)[k] + ']}'
                random_band_list[complete_random_number + i] = band_str

            for i in range(least_random_number):
                num_bands = random.randrange(1, 19, 1)
                if num_bands // 2 >= len(ext_ref_band_list):
                    num_ext_bands = len(ext_ref_band_list)
                    num_aux_bands = num_bands - num_ext_bands
                else:
                    num_aux_bands = num_bands // 2
                    num_ext_bands = num_bands - num_aux_bands
                temp_ext_band_list = random.sample(ext_ref_band_list, num_ext_bands)
                temp_aux_band_list = random.sample(aux_band_list, num_aux_bands)
                temp_complete_band_list = basic_ref_band_list + temp_ext_band_list + temp_aux_band_list
                for k in range(len(temp_complete_band_list)):
                    if k == 0:
                        band_str = '{"bands":[' + (temp_complete_band_list)[k]
                    elif (k > 0 and k < len(temp_complete_band_list) - 1):
                        band_str += ',' + (temp_complete_band_list)[k]
                    else:
                        band_str += ',' + (temp_complete_band_list)[k] + ']}'
                random_band_list[
                    complete_random_number + less_random_number + i] = band_str
            with open(DOWNLOAD_FOLDER + 'variables/bands.pkl', 'wb') as f:
                pickle.dump(random_band_list, f)

    return random_band_list


def define_bands(DOWNLOAD_FOLDER, randomize, random_granule_number, basic_ref_band_list,
                 ext_ref_band_list, aux_band_list, static_band):
    random_granule_bands = band_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number,
                                           basic_ref_band_list, 
                                           ext_ref_band_list, aux_band_list)
    bands = {}
    bands.update(static_band)
    for k in range(random_granule_number):
        if k + len(static_band) + 1 < 10:
            bands.update({'0' + str(k + len(static_band) + 1):
                              random_granule_bands[k]})
        else:
            bands.update({str(k + len(static_band) + 1):
                              random_granule_bands[k]})
    return bands


def define_coordinates(static_granule_list, random_ids, static_granule_dict,
                       random_granule_dict):
    ids = static_granule_list + random_ids
    count = len(ids)
    coordinates={}
    for i in range(count):
        if i < 4:
            coordinates.update({'0' + str(i+1): static_granule_dict[ids[i][1:]]})
        elif i < 9:
            coordinates.update({'0' + str(i + 1): random_granule_dict[ids[i][1:]]})
        else:
            coordinates.update({str(i + 1): random_granule_dict[ids[i][1:]]})
    return coordinates


def period_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, period_list):
    if randomize:
        random_period_list = [''] * random_granule_number
        for i in range(random_granule_number):
            random_period_list[i] = (random.sample(period_list, 1))[0]
        with open(DOWNLOAD_FOLDER + 'variables/periods.pkl', 'wb') as f:
            pickle.dump(random_period_list, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/periods.pkl', 'rb') as f:
                random_period_list = pickle.load(f)
        except FileNotFoundError:
            print('Periods do not exist, start randomizing')
            random_period_list = [''] * random_granule_number
            for i in range(random_granule_number):
                random_period_list[i] = (random.sample(period_list, 1))[0]
            with open(DOWNLOAD_FOLDER + 'variables/periods.pkl', 'wb') as f:
                pickle.dump(random_period_list, f)

    return random_period_list


def define_periods(DOWNLOAD_FOLDER, randomize, random_granule_number, period_list, static_periods):
    random_granule_period = period_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, period_list)
    periods = {}
    periods.update(static_periods)
    for k in range(random_granule_number):
        if k + len(static_periods) + 1 < 10:
            periods.update({'0' + str(k + len(static_periods) + 1):
                                    random_granule_period[k]})
        else:
            periods.update({str(k + len(static_periods) + 1):
                                    random_granule_period[k]})
    return periods

def strTimeProp(start, end, format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formated in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))

def randomDate(start, end, prop, periods, counter_int):
    if counter_int + 5 < 10:
        counter = '0' + str(counter_int + 5)
    else:
        counter = str(counter_int + 5)
    random_date_string = strTimeProp(start, end, '%Y-%m-%dT%H:%M:%S', prop)
    random_date = datetime.strptime(random_date_string, '%Y-%m-%dT%H:%M:%S')
    if periods[counter] == 'YEAR':
        selected_random_date = random_date.strftime("%Y-01-01T00:00:01")
    elif periods[counter] == 'QUARTER':
        if int(random_date_string[5:7]) < 4:
            selected_random_date = random_date.strftime("%Y-01-01T00:00:01")
        elif int(random_date_string[5:7]) < 7:
            selected_random_date = random_date.strftime("%Y-04-01T00:00:01")
        elif int(random_date_string[5:7]) < 10:
            selected_random_date = random_date.strftime("%Y-07-01T00:00:01")
        else:
            selected_random_date = random_date.strftime("%Y-10-01T00:00:01")
    elif periods[counter] == 'MONTH':
        selected_random_date = random_date.strftime("%Y-%m-01T00:00:01")
    elif periods[counter] == 'TENDAYS':
        if int(random_date_string[8:10]) < 11:
            selected_random_date = random_date.strftime("%Y-%m-01T00:00:01")
        elif int(random_date_string[8:10]) < 21:
            selected_random_date = random_date.strftime("%Y-%m-11T00:00:01")
        else:
            selected_random_date = random_date.strftime("%Y-%m-21T00:00:01")
    else:
        selected_random_date = random_date.strftime("%Y-%m-%dT00:00:01")

    return selected_random_date

def date_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, periods):
    today = datetime.now()
    today_minus_month = (today - relativedelta(months=+1)).strftime("%Y-%m-%dT%H:%M:%S")
    if randomize:
        random_date_list = [''] * random_granule_number
        for i in range(random_granule_number):
            random_date_list[i] = randomDate("2017-04-01T00:00:00", today_minus_month,
               random.random(), periods, i)
        with open(DOWNLOAD_FOLDER + 'variables/dates.pkl', 'wb') as f:
            pickle.dump(random_date_list, f)
    else:
        try:
            with open(DOWNLOAD_FOLDER + 'variables/dates.pkl', 'rb') as f:
                random_date_list = pickle.load(f)
        except FileNotFoundError:
            print('dates do not exist, start randomizing')
            random_date_list = [''] * random_granule_number
            for i in range(random_granule_number):
                random_date_list[i] = randomDate("2017-04-01T00:00:00", today_minus_month,
               random.random(), periods, i)
            with open(DOWNLOAD_FOLDER + 'variables/dates.pkl', 'wb') as f:
                pickle.dump(random_date_list, f)

    return random_date_list


def define_dates(DOWNLOAD_FOLDER, randomize, random_granule_number, static_dates, periods):
    random_granule_date = date_randomizer(DOWNLOAD_FOLDER, randomize, random_granule_number, periods)
    dates = {}
    dates.update(static_dates)
    for k in range(random_granule_number):
        if k + len(static_dates) + 1 < 10:
            dates.update({'0' + str(k + len(static_dates) + 1):
                                    random_granule_date[k]})
        else:
            dates.update({str(k + len(static_dates) + 1):
                                    random_granule_date[k]})
    return dates


def define_request_parameters(DOWNLOAD_FOLDER, randomize, static_granule_list,
                              random_granule_number, random_ids,
                              static_granule_format, image_formats,
                              resolution_list, static_resolution, 
                              coordinate_system_list, static_projection,
                              basic_ref_band_list, ext_ref_band_list, 
                              aux_band_list, static_band, period_list, 
                              static_periods, static_dates):

    num_products = 4 + len(random_ids)
    names = define_names(static_granule_list, random_granule_number, random_ids)
    format = define_format(DOWNLOAD_FOLDER, randomize, static_granule_format,
                           random_granule_number, image_formats)
    resolutions = define_resolutions(DOWNLOAD_FOLDER, randomize,
                                     random_granule_number, resolution_list,
                                     static_resolution)
    projections = define_projections(DOWNLOAD_FOLDER, randomize,
                                     random_granule_number, coordinate_system_list,
                                     static_projection)
    bands = define_bands(DOWNLOAD_FOLDER, randomize, random_granule_number,
                         basic_ref_band_list, ext_ref_band_list, aux_band_list,
                         static_band)
    coordinates = define_coordinates(static_granule_list, random_ids,
                                     static_granule_dict, random_granule_dict)
    periods = define_periods(DOWNLOAD_FOLDER, randomize, random_granule_number, period_list, static_periods)

    dates = define_dates(DOWNLOAD_FOLDER, randomize, random_granule_number, static_dates, periods)

    request_parameters = [names, format, resolutions, projections, bands, coordinates, periods, dates]
    return request_parameters, num_products


def get_parameters(DOWNLOAD_FOLDER, RANDOMIZE):
    if not os.path.exists(DOWNLOAD_FOLDER + 'variables/'):
        os.makedirs(DOWNLOAD_FOLDER + 'variables/')

    with open(DOWNLOAD_FOLDER + 'variables/static_parameters_variables.pkl', 'wb') as f:
        pickle.dump(DOWNLOAD_FOLDER, f)
        pickle.dump(static_granule_list, f)
        pickle.dump(static_granule_dict, f)
        pickle.dump(random_granule_number, f)
        pickle.dump(random_granule_list, f)
        pickle.dump(random_granule_dict, f)
        pickle.dump(static_granule_format, f)
        pickle.dump(image_formats, f)
        pickle.dump(resolution_list, f)
        pickle.dump(static_resolution, f)
        pickle.dump(coordinate_system_list, f)
        pickle.dump(static_projection, f)
        pickle.dump(basic_ref_band_list, f)
        pickle.dump(ext_ref_band_list, f)
        pickle.dump(aux_band_list, f)
        pickle.dump(static_band, f)
        pickle.dump(period_list, f)
        pickle.dump(static_periods, f)
        pickle.dump(static_dates, f)

    random_ids = granule_randomizer(DOWNLOAD_FOLDER, RANDOMIZE, random_granule_number,
                                    random_granule_list)
    request_parameters, num_products = define_request_parameters(DOWNLOAD_FOLDER, RANDOMIZE,
                                                   static_granule_list,
                                                   random_granule_number,
                                                   random_ids,
                                                   static_granule_format,
                                                   image_formats,
                                                   resolution_list,
                                                   static_resolution,
                                                   coordinate_system_list,
                                                   static_projection,
                                                   basic_ref_band_list,
                                                   ext_ref_band_list,
                                                   aux_band_list, static_band, 
                                                   period_list, static_periods, 
                                                   static_dates)

    # test:
    # i = 1
    # print(request_parameters[0]["{0:0=2d}".format(i)])
    # print(request_parameters[1]["{0:0=2d}".format(i)])

    return request_parameters, num_products

if __name__ == '__main__':
    get_parameters(DOWNLOAD_FOLDER, RANDOMIZE)
