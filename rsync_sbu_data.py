#!/bin/csh

cd /home/disk/bob/impacts/gdrive/IMPACTS

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'Jan_25*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/airmarweather/netcdf/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200128*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/chm15k/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'GrawSonde_RTS_20200126*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/grawmetsounding/netcdf/

#NEW 20200128
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/mrrpro2white/netcdf/202001/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'parsivel_20200127*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/parsivel2/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200127*' http://doppler.somas.stonybrook.edu/IMPACTS/dopplerlidar/netcdf/2020/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '2020*' http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200106/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200107/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200108/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200118/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200119/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200125/
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20200126/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200127*' http://doppler.somas.stonybrook.edu/IMPACTS/mrr2/netcdf/202001/

#NEW 20200128
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/mrrpro2/netcdf/202001/

#DOES THIS EXIST OR IS MOBILE TRUCK ONLY ONE
#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/mrrpro2white/netcdf/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '2020-*' http://doppler.somas.stonybrook.edu/IMPACTS/mwr/csv/

#NEW 20200128
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/parsivel/netcdf/2020/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/parsivel2/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200127*' http://doppler.somas.stonybrook.edu/IMPACTS/pluvio/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/roger/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200127*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo7.5k/netcdf/2020/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'L1__2020*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo15k/netcdf/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'L2__2020012*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo15k/netcdf/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'L3_DEFAULT__2020012*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo15k/netcdf/

