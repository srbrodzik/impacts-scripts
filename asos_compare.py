import pandas as pd

indir = '/home/disk/funnel/impacts-website/data_archive/asos_test'
field_file = 'ops.asos.20200208.kbgm.field.csv'
qc_file = 'IMPACTS_ASOS_20200208_kbgm_qc.csv'

df_field = pd.read_csv(indir+'/'+field_file)
df_qc = pd.read_csv(indir+'/'+qc_file)

precip_intervals_field = df_field.iloc[:,5].dropna()
precip_intervals_field_nonzero = precip_intervals_field[precip_intervals_field > 0]
precip_accum_field = df_field.iloc[:,4].dropna()
precip_accum_field_nonzero = precip_accum_field[precip_accum_field > 0]
daily_accum_precip_field = float(precip_intervals_field.sum())
data_precip_int_field = list(df_field.iloc[-1,:].values)
data_precip_int_field[5] = str(daily_accum_precip_field)

precip_intervals_qc = df_qc.iloc[:,5].dropna()
precip_intervals_qc_nonzero = precip_intervals_qc[precip_intervals_qc > 0]
precip_accum_qc = df_qc.iloc[:,4].dropna()
precip_accum_qc_nonzero = precip_accum_qc[precip_accum_qc > 0]
daily_accum_precip_qc = float(precip_intervals_qc.sum())
data_precip_int_qc = list(df_qc.iloc[-1,:].values)
data_precip_int_qc[5] = str(daily_accum_precip_qc)

