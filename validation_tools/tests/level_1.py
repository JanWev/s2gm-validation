


"""
Level X test no. Y: ...
"""
def level_X_Y(test_metadata):
    test_result = {
        'test_id': 'level_X_Y',
        'test_name': '...',
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