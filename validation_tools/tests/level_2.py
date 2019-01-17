# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Make L0 tests.
"""

from validation_tools.utilities import validation_metadata
from pathlib import Path
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