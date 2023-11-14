#!/usr/bin/env python
'''
extract non-default parameters for publishing
'''

from pymavlink import mavparm
import fnmatch
import sys

from argparse import ArgumentParser
parser = ArgumentParser(description=__doc__)
parser.add_argument("defaults", metavar="defaults")
parser.add_argument("params", metavar="params")

args = parser.parse_args()

p1 = mavparm.MAVParmDict()
p2 = mavparm.MAVParmDict()
p1.load(args.defaults)
p2.load(args.params)

include_list = ['Q_ENABLE', 'Q_FRAME*', 'AFS_*']
exclude_list = ['AHRS_TRIM_?',
                '*GND_PRESS',
                'COMPASS_EXTERN*',
                'COMPASS_DEC',
                'COMPASS_DIA*',
                'COMPASS_ODI*',
                '*_ABS_PRESS',
                'SR?_*',
                'STAT_*',
                'SYS_NUM_RESETS',
                '*_DEV_ID',
                '*_DEVID', ]

# For physical aircraft, we don't want to publish compass or accel calibrations
if "SIM_OPOS_LAT" not in p2:
    exclude_list.extend(['COMPASS_OFS*', '', 'INS_*OFFS_?', 'INS_*SCAL_?'])

def in_list(p, lst):
    for e in lst:
        if fnmatch.fnmatch(p, e):
            return True
    return False

def vstring(v):
    s = str(v)
    if s.find('.'):
        while s[-1] == '0':
            s = s[:-1]
    if s[-1] == '.':
        s = s[:-1]
    return s

for p in p2:
    if in_list(p, exclude_list) and not in_list(p, include_list):
        continue
    if not p in p1:
        sys.stderr.write("WARNING: {} not found in defaults\n".format(p))
        continue
    if (p1[p] == p2[p] and not in_list(p, include_list)):
        continue

    print("%s,%s" % (p, vstring(p2[p])))
