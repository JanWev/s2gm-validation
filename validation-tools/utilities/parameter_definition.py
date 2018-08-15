import random
import pickle
from .basic_parameters import granule_number, granule_list, granule_dict

RANDOMIZE = False  # This can be set to True if you like to create a new set of random Granules

def granule_randomizer(randomize, granule_number):
    if randomize:
        random_ids = random.sample(granule_list, granule_number)
        with open('ids.pkl', 'wb') as f:
            pickle.dump(random_ids, f)
    else:
        try:
            with open('ids.pkl', 'rb') as f:
                random_ids = pickle.load(f)
        except FileNotFoundError:
            print('IDs do not exist, start randomizing')
            random_ids = random.sample(granule_list, granule_number)
            with open('ids.pkl', 'wb') as f:
                pickle.dump(random_ids, f)

    return random_ids

def define_request_parameters():
    # 4 fix requests
    data_01 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 10}'
    data_02 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "YEAR", "resolution": 20}'
    data_03 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "QUARTER", "resolution": 10}'
    data_04 = '{"tileId": "30VWJ", "startDate":"2018-03-01T00:00:00", "temporalPeriod": "MONTH", "resolution": 60}'



def main():
    random_ids = granule_randomizer(RANDOMIZE, granule_number)
    define_request_parameters(random_ids)

if __name__ == '__main__':
    main()