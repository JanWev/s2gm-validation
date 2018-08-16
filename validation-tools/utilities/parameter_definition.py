from datetime import datetime
import random
import pickle
from .static_parameters import static_granule_list, static_granule_dict, \
    random_granule_number, random_granule_list, random_granule_dict, \
    static_granule_format, image_formats, resolution_list, \
    coordinate_system_list, band_list

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

RANDOMIZE = False  # This can be set to True if you like to create a new set of random Granules

def granule_randomizer(randomize, random_granule_number, random_granule_list):
    if randomize:
        random_ids = random.sample(random_granule_list, random_granule_number)
        with open('ids.pkl', 'wb') as f:
            pickle.dump(random_ids, f)
    else:
        try:
            with open('ids.pkl', 'rb') as f:
                random_ids = pickle.load(f)
        except FileNotFoundError:
            print('IDs do not exist, start randomizing')
            random_ids = random.sample(random_granule_list, random_granule_number)
            with open('ids.pkl', 'wb') as f:
                pickle.dump(random_ids, f)

    return random_ids

def define_names(static_granule_list, random_granule_number, random_ids):
    names = {}
    for i in range(len(static_granule_list)):
        names.update({'0' + str(i + 1): 'S2GM_validation_request_'
                         + str(datetime.now().strftime("%Y%m%dT%H%M%S")) +
                         '_static_0' + str(i + 1) + '_' +
                         str(static_granule_list[i])})

    for k in range(random_granule_number):
        names.update({'0' + str(k + len(static_granule_list) + 1): 'S2GM_validation_request_'
                                        + str(
            datetime.now().strftime("%Y%m%dT%H%M%S")) +
                                        '_random_0' + str(k + 1) + '_' +
                                        str(random_ids[k])})

        return names


def format_randomizer(randomize, random_granule_number,
                      image_formats):
    if randomize:
        format_list = ['']*random_granule_number
        for i in range(random_granule_number):
            format_list[i] = (random.sample(image_formats, 1))[0]
            with open('formats.pkl', 'wb') as f:
                pickle.dump(format_list, f)
    else:
        try:
            with open('formats.pkl', 'rb') as f:
                format_list = pickle.load(f)
        except FileNotFoundError:
            print('Formats do not exist, start randomizing')
            format_list = [''] * random_granule_number
            for i in range(random_granule_number):
                format_list[i] = (random.sample(image_formats, 1))[0]
                with open('formats.pkl', 'wb') as f:
                    pickle.dump(format_list, f)

    return format_list

def define_format(randomize, static_granule_format, random_granule_number,
                      image_formats):
    random_granule_format = format_randomizer(randomize, random_granule_number,
                      image_formats)
    formats = {}
    formats.update(static_granule_format)
    for k in range(random_granule_number):
        formats.update({'0' + str(k + len(static_granule_format) + 1): random_granule_format[k]})

    return formats

# def parameter_randomizer(random_ids):
#     x = 1 # test


def define_request_parameters(randomize, static_granule_list,
                              random_granule_number, random_ids,
                              static_granule_format, image_formats):
    # 4 fix requests
    data_01 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 10}'
    data_02 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "YEAR", "resolution": 20}'
    data_03 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "QUARTER", "resolution": 10}'
    data_04 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 60}'

    names = define_names(static_granule_list, random_granule_number, random_ids)
    format = define_format(randomize, static_granule_format,
                           random_granule_number, image_formats)
    resolutions = define_resolutions()

    request_parameters = [names, format]
    return request_parameters


def main():
    random_ids = granule_randomizer(RANDOMIZE, random_granule_number,
                                    random_granule_list)
    request_parameters = define_request_parameters(RANDOMIZE,
                                                   static_granule_list,
                                                   random_granule_number,
                                                   random_ids,
                                                   static_granule_format,
                                                   image_formats)

    # test:
    # i = 1
    # print(request_parameters[0]["{0:0=2d}".format(i)])
    # print(request_parameters[1]["{0:0=2d}".format(i)])

    return request_parameters

if __name__ == '__main__':
    main()