#!/bin/csh

cd /home/disk/bob/impacts/radar/sbu

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'Jan_01' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/airmarweather/netcdf/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/chm15k/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'GrawSonde_RTS_2020027*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/grawmetsounding/netcdf/

#NEW 20200128
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/mrrpro2white/netcdf/202002/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'parsivel_20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/parsivel2/netcdf/2020/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/dopplerlidar/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/images/quicklooks/
#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200227/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/mrr2/netcdf/202002/

#NEW 20200128
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/mrrpro2/netcdf/202002/

#DOES THIS EXIST OR IS MOBILE TRUCK ONLY ONE
#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/mrrpro2white/netcdf/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '2020-01-30*' http://doppler.somas.stonybrook.edu/IMPACTS/mwr/csv/**

#NEW 20200128
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/parsivel/netcdf/2020/

#NEW 20200207
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/parsivel2/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/pluvio/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/roger/
####
#NEW 20200129  REDOWNLOAD 20200205 images
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/skyler/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo7.5k/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo15k/netcdf/

#NEW 20200130
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '2020-02-27*' http://doppler.somas.stonybrook.edu/IMPACTS/weatherdhs/csv/

