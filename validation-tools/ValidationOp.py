# !/usr/bin/python
# -*- coding: UTF-8 -*-
""" Purpose: Orchestrate download and the validation of s2gm products.
"""

import sys
import argparse
import logging
from datetime import datetime
from .utilities import parameter_definition

__author__ = 'jan wevers - jan.wevers@brockmann-consult.de'

def log_inputs(tests):
    logging.basicConfig(filename='execution.log', filemode='a',level=logging.DEBUG)
    logging.info('ValidationOp executed: %s', str(datetime.now()))
    logging.debug('Requested tests by the user: %s', str(tests))


def main(tests):
    log_inputs(tests)
    request_parameters = parameter_definition.main()


    # Tests to be executed here:
    ## L0
    ## L1
    ## L2


if __name__ == "__main__":
    #input_one = sys.argv[1]
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--tests",# name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=int,
        default=[1, 2, 3], # default if nothing is provided
        help='index numbers of wanted tests. usage: --tests 1 2 5 6. default --tests 1 2 3'
    )
    # parse the command line
    args = CLI.parse_args()
    main(args.tests)