#!/usr/bin/python3

import os
import shutil

# full url = base/YYYY/MM/DD/ql
# file name = WFF_MRR2-03_YYYY_MMDD_hh_ql.png (hourly)
mrrBaseUrl = 'https://wallops-prf.gsfc.nasa.gov/Field_Campaigns/IMPACTS/Plots/MRR2-03'

# full url = base/YYYY
# file name = WFF_apu18_YYYY_MMDD_rain.png
parsivelRainBaseUrl = 'https://wallops-prf.gsfc.nasa.gov/Disdrometer/Parsivel/apu18/Plots/Rain'

# full url = base/YYYY
# file name = WFF_apu18_YYYY_MMDD_dsd.png
parsivelDSDbaseUrl = 'https://wallops-prf.gsfc.nasa.gov/Disdrometer/Parsivel/apu18/Plots/DSD'

# file name = AIO_YYYY_MMDD.png (current day has 'latest' in place of 'YYYY_MMDD'
AIObaseUrl = 'https://wallops-prf.gsfc.nasa.gov/All-in-1/Plots/AIO_latest.png
