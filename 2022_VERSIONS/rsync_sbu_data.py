#!/bin/csh

cd /home/disk/bob/impacts/radar/sbu

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'Jan_01' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/airmarweather/netcdf/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/chm15k/netcdf/2022/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'GrawSonde_RadarTruck_RTS_2022*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/grawmetsounding/netcdf/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/mrrpro2white/netcdf/202002/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'parsivel_2022*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/parsivel2/netcdf/2022/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'QUNS_ppi_2022*' http://doppler.somas.stonybrook.edu/IMPACTS/RadarTruck/skyler2/netcdf/20220117/ppi

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20220227*' http://doppler.somas.stonybrook.edu/IMPACTS/dopplerlidar/netcdf/2022/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'GrawSonde_SBUSouthP*' http://doppler.somas.stonybrook.edu/IMPACTS/grawmetsounding/netcdf/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'imageset_2022*' http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/images/quicklooks/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/kaspr/netcdf/20220227/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*2022*' http://doppler.somas.stonybrook.edu/IMPACTS/mrr2/netcdf/202201/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20220227*' http://doppler.somas.stonybrook.edu/IMPACTS/mrrpro2/netcdf/202202/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/mrrpro2white/netcdf/202202/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '2020-01-30*' http://doppler.somas.stonybrook.edu/IMPACTS/mwr/csv/**

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'parsivel*' http://doppler.somas.stonybrook.edu/IMPACTS/parsivel/netcdf/2022/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20220227*' http://doppler.somas.stonybrook.edu/IMPACTS/parsivel2/netcdf/2022/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A 'pluvio2_2022*' http://doppler.somas.stonybrook.edu/IMPACTS/pluvio/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/roger/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/skyler/

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 http://doppler.somas.stonybrook.edu/IMPACTS/skyler1/netcdf/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*20200227*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo7.5k/netcdf/2022/

#----------------------- TO HERE ---------------------------

wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '*_2022*' http://doppler.somas.stonybrook.edu/IMPACTS/vceilo15k/netcdf/

#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=1 -A '2022-02-27*' http://doppler.somas.stonybrook.edu/IMPACTS/weatherdhs/csv/

