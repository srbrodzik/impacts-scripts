#! /bin/csh
#

cd /home/disk/bob/impacts/bin

python ./process_nexrad_data.py |& \
    LogFilter -d $HOME/logs -p process_nexrad_data -i impacts >& /dev/null &
