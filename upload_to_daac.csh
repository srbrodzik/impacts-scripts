Go to directory where files to be uploaded live

lftp impacts@ghrc.nsstc.nasa.gov
Password: snowfallATLANTIC2020!

set ssl:verify-certificate no

ls - gives dir listing

cd to appropriate directory

mirror -R

or

mirror -R '*ch01*'


# Non-interactive command
lftp -c "open ftp://impacts:snowfallATLANTIC2020\!@ghrc.nsstc.nasa.gov; cd MRMS; cd BaseDBZ; mirror -R"
