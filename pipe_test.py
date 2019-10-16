# To read in csv from standard input
# python pipe_test.py < [csv file]

import sys
import pandas as pd

df = pd.read_csv(sys.stdin)
print df
