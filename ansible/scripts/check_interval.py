#!/usr/bin/env python
#
# Computes the optimal interpreter check interval for the machine it is run on

import sys
import math

from test import pystone


def checkinterval():
    # Computes the optimal interpreter checkinterval
    # as advised on zope-dev: pystones / 50.

    tries = 100
    stones = []

    for i in range(tries):
        stones.append(pystone.pystones()[1])
        print(stones[-1])

    raw = reduce(lambda x,y: x+y, stones, 0.0) / (50.0*tries)
    return int(math.ceil(raw))


def main():
    print("Computing the optimal interpreter check interval...")
    print("python-check_interval: {}".format(checkinterval()))
    sys.exit(0)


if __name__ == '__main__':
    main()
