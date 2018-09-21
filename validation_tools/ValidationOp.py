# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate validation of s2gm products.
"""

import logging
import argparse
from datetime import datetime, date

__author__ = 'jan wevers, tanja gasber & florian girtler - jan.wevers@brockmann-consult.de, gasber@geoville.com, girtler@geoville.com'

def log_inputs(tests):
    try:
        logging.basicConfig(filename='./logs/execution.log', filemode='a',level=logging.DEBUG)
        logging.info('ValidationOp executed: %s', str(datetime.now()))
        logging.debug('Requested tests by the user: %s', str(tests))
    except FileNotFoundError:
        print('log file does not exist and will be created')
        f = open('./logs/execution.log')
        f.close()
        logging.basicConfig(filename='./logs/execution.log', filemode='a', level=logging.DEBUG)
        logging.info('ValidationOp executed: %s', str(datetime.now()))
        logging.debug('Requested tests by the user: %s', str(tests))


def main(tests):
    log_inputs(tests)
    # trigger L0 to L3 tests

if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--tests",
        nargs="*",
        type=int,
        default=[1, 2, 3],
        help='index numbers of wanted tests. usage: --tests 1 2 5 6. default --tests 1 2 3'
    )
    args = CLI.parse_args()
    main(args.tests)