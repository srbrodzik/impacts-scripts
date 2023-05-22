#!/bin/csh

set date = "`date -u --date=yesterday +'%Y%m%d'`"
echo $date

# IMAGES
cd /home/disk/bob/impacts/radar/sbu_images/mrrpro2white
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A 'mrrprowhite_realtime' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/mrrpro2white/images/quicklooks/
/bin/cp *.png forCatalog
cd forCatalog
mmv "mrrprowhite_realtime_*.png" "radar.MRR.#1\0\0\0\0.Brookhaven_NY_time_ht.png"
foreach file (*.png)
    /home/disk/bob/impacts/bin/ftpToNCAR.py $file
end	    

cd /home/disk/bob/impacts/radar/sbu_images/mwr-mp3000a
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A 'mwrmp3000*' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/mwr_mp3000a/images/quicklooks/
/bin/cp *.png forCatalog
cd forCatalog
mmv "mwrmp3000A_*.png" "upperair.MWR.#1\0\0\0\0.Brookhaven_NY.png"
foreach file (*.png)
    /home/disk/bob/impacts/bin/ftpToNCAR.py $file
end	    

cd /home/disk/bob/impacts/radar/sbu_images/parsivel
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A 'parsivel*' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/parsivel/images/quicklooks/
/bin/cp *.png forCatalog
cd forCatalog
mmv "parsivel_realtime_*.png" "surface.Parsivel.#1\0\0\0\0.Brookhaven_NY.png"
foreach file (*.png)
    /home/disk/bob/impacts/bin/ftpToNCAR.py $file
end	    

cd /home/disk/bob/impacts/radar/sbu_images/pluvio
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A 'pluvio*' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/pluvio/images/quicklooks/
/bin/cp *.png forCatalog
cd forCatalog
mmv "pluvio_*.png" "surface.Pluvio.#1\0\0\0\0.Brookhaven_NY.png"
foreach file (*.png)
    /home/disk/bob/impacts/bin/ftpToNCAR.py $file
end	    

cd /home/disk/bob/impacts/radar/sbu_images/vceilo15k
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A 'cl51*' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/vceilo15k/images/quicklooks/
/bin/cp *.png forCatalog
cd forCatalog
mmv "cl51_*.png" "lidar.Ceilometer.#1\0\0\0\0.Brookhaven_NY_15000m.png"
foreach file (*.png)
    /home/disk/bob/impacts/bin/ftpToNCAR.py $file
end	    

cd /home/disk/bob/impacts/radar/sbu_images/wcr
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A 'WACR*' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/wcr/images/quicklooks/
/bin/cp *.png forCatalog
cd forCatalog
./renameFiles.py
foreach file (*.png)
    /home/disk/bob/impacts/bin/ftpToNCAR.py $file
end	    

# DATA
cd /home/disk/bob/impacts/radar/sbu/mrrpro2white
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A '*nc' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/mrrpro2white/netcdf/202301/20230101/
#cd /home/disk/bob/impacts/radar/sbu/mwr-mp3000a
#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=5 -A '*nc' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/mwr_mp3000a/netcdf/202301/20230101/
cd /home/disk/bob/impacts/radar/sbu/parsivel
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=4 -A '*nc' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/parsivel/netcdf/
cd /home/disk/bob/impacts/radar/sbu/pluvio
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=4 -A '*txt' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/pluvio/csv/
cd /home/disk/bob/impacts/radar/sbu/vceilo15k
wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=4 -A '*nc' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/vceilo15k/netcdf/
#cd /home/disk/bob/impacts/radar/sbu/wcr
#wget -r --user DataAccess --password WinterAtSBU --no-parent -nH --cut-dirs=4 -A '*nc' http://doppler.somas.stonybrook.edu/IMPACTS/BNL/wcr/netcdf/

