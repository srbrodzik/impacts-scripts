#!/usr/bin/python3

# These files are updated every minute or two and overwrite the previous
# version.  We could get them in realtime every 5 minutes or so and then
# replace them after each mission with more accurate processed data.
# POC is Rachael Kroodsma

import os

url = 'https://terpconnect.umd.edu/~rkroodsm/impacts/kmz'

# For each channel there are two types of files
#     full flight - cosmir_<channel>.kmz
#     last 30 min - cosmir_<channel>_last30.kmz
channels = ['50','52','89PD','89h','89v','165PD','165h','165v',
            '183_1','183_3','183_7']
