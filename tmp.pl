#!/usr/bin/perl

$ENV{'PYTHONPATH'} = "/home/disk/bob/impacts/bin:/home/disk/shear2/brodzik/python:/usr/local/lib/python2.7/dist-packages:".$ENV{'PYTHONPATH'};
$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin";

#$ENV{'LD_LIBRARY_PATH'} = "/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin:/opt/intel//compilers_and_libraries_2019.1.144/linux/mpi/intel64/libfabric/lib:/opt/intel//compilers_and_libraries_2019.1.144/linux/mpi/intel64/lib/release:/opt/intel//compilers_and_libraries_2019.1.144/linux/mpi/intel64/lib:/opt/intel/compilers_and_libraries_2019.1.144/linux/ipp/lib/x86_64:/opt/intel/compilers_and_libraries_2019.1.144/linux/compiler/lib/intel64_lin:/opt/intel/compilers_and_libraries_2019.1.144/linux/mkl/lib/intel64_lin:/opt/intel/compilers_and_libraries_2019.1.144/linux/tbb/lib/intel64/gcc4.7:/opt/intel/compilers_and_libraries_2019.1.144/linux/tbb/lib/intel64/gcc4.7:/opt/intel/debugger_2019/libipt/intel64/lib:/opt/intel/compilers_and_libraries_2019.1.144/linux/daal/lib/intel64_lin:/opt/intel//compilers_and_libraries_2019.1.144/linux/mpi/intel64/lib:/opt/intel/composer_xe_2013_sp1.4.211/compiler/lib/intel64:/opt/intel/mic/coi/host-linux-release/lib:/opt/intel/mic/myo/lib:/opt/intel/composer_xe_2013_sp1.4.211/mpirt/lib/intel64:/opt/intel/composer_xe_2013_sp1.4.211/ipp/../compiler/lib/x86_64:/opt/intel/composer_xe_2013_sp1.4.211/ipp/lib/x86_64:/opt/intel/mic/coi/host-linux-release/lib:/opt/intel/mic/myo/lib:/opt/intel/composer_xe_2013_sp1.4.211/compiler/lib/intel64:/opt/intel/composer_xe_2013_sp1.4.211/mkl/lib/intel64:/opt/intel/composer_xe_2013_sp1.4.211/tbb/lib/intel64/gcc4.1:/opt/intel/Compiler/11.1/064/mkl/lib/em64t:/opt/intel/Compiler/11.1/064/ipp/em64t/sharedlib:/opt/intel/Compiler/11.1/064/lib/intel64:/opt/intel/Compiler/11.1/064/ipp/em64t/sharedlib:/opt/intel/Compiler/11.1/064/mkl/lib/em64t:/opt/intel/Compiler/11.1/064/tbb/intel64/cc4.1.0_libc2.4_kernel2.6.16.21/lib:/opt/intel/Compiler/11.1/064/lib/intel64:/opt/intel/Compiler/11.1/064/ipp/em64t/sharedlib:/opt/intel/Compiler/11.1/064/mkl/lib/em64t:/opt/intel/Compiler/11.1/064/tbb/intel64/cc4.1.0_libc2.4_kernel2.6.16.21/lib:/usr/pgi/linux86/5.0/lib:/usr/pgi/linux86/lib:/usr/local/lib";

$command = "umask 2";
system($command);

$command = "/usr/bin/python /home/disk/bob/impacts/bin/skewplot.py --file /home/disk/funnel/impacts/archive/ops/text_sounding/20190731/ops.text_sounding.201907310000.CHH.html.new --outpath /tmp --format UWYO";
system($command);