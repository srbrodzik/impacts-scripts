#!/usr/bin/python3

import pandas as pd

pickleDir = '/home/disk/bob/impacts/bin/pickle_jar'

pickleFile = 'nysm_2021.pkl'
site_info_2021 = pd.read_pickle(pickleDir+'/'+pickleFile)

## Compare to 2020 data to see if data is the same -- it is
#pickleFile = 'nysm.pkl'
#site_info_2020 = pd.read_pickle(pickleDir+'/'+pickleFile)
#site_info_2020.equals(site_info_2021)
