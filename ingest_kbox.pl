#!/usr/bin/perl

use File::Copy;

#define pathnames
$RAWPATH = "/home/disk/data/gempak/nexrad/craft/KBOX";
$WORKPATH = "/home/disk/bob/impacts/data.server/raw/kbox/sur";
$CFRADPATH = "/home/disk/bob/impacts/data.server/cfradial/kbox/sur";
#$ZEBPATH = "/home/disk/bob/olympex/zebra/moments/kbox/sur";
$BINPATH = "/home/disk/blitz/bin";

unless (-e $WORKPATH."/TEMP-cfradFiles") {mkdir $WORKPATH."/TEMP-cfradFiles";}
unless (-e $WORKPATH."/TEMP-zebFiles") {mkdir $WORKPATH."/TEMP-zebFiles";}

while (1)  {

    # Get date and time information
    $yesterday = `date -u --date='1 day ago' "+%Y%m%d"`;
    chop $yesterday;
    $yesterdayDir = $WORKPATH."/".$yesterday;
    unless (-e $yesterdayDir) {mkdir $yesterdayDir;}

    $today = `date -u "+%Y%m%d"`;
    chop $today;
    $todayDir = $WORKPATH."/".$today;
    unless (-e $todayDir) {mkdir $todayDir;}

    $last_hour = `date -u --date='1 hour ago' "+%H"`;
    chop $last_hour;
    $curr_hour = `date -u "+%H"`;
    chop $curr_hour;

    # Create find command
    if ($curr_hour eq "00") {
		$queryString1 = "KBOX_".$yesterday."_23??";
		$queryString2 = "KBOX_".$today."_00??";
    }
    else {
		$queryString1 = "KBOX_".$today."_".$last_hour."??";
		$queryString2 = "KBOX_".$today."_".$curr_hour."??";
    }
    $findcmd = "/usr/bin/find -type f -follow \\( -iname \"$queryString1\" -or -iname \"$queryString2\" \\) -print";
    #print "findcmd = $findcmd\n";

    # Get new kbox level II data
    chdir($RAWPATH);
    open(FIND,"$findcmd |");
    while(<FIND>) {
		chop $_;
		print "top of while loop: $_ ";
		$under_pos = index($_,"_");
		$date = substr($_,$under_pos+1,8);
		print "date = $date\n";
		unless (-e $WORKPATH."/".$date."/".$_) {
		    print "   new file . . . copy to working dir\n";
			copy($_,$WORKPATH);
		}
    }

    # Change to working directory and set env var
    chdir($WORKPATH);
    #$ENV{ZEB_SOCKET} = '/tmp/zeb.bob.meso.socket';

    # Uncompress kbox files, remove ancillary nc files, save original compressed files
    foreach $compFile (<KBOX_????????_????>) {
		print "compFile = $compFile\n";
		$date = substr($compFile,5,8);
		$command = "java -classpath /home/disk/freshair_ldm/local/java/netcdfAll-4.6.jar ucar.nc2.FileWriter2 -in ".$compFile." -out ".$compFile.".nc";
		#print "command = $command\n";
		system($command);
		unlink $compFile.".nc";
		if (-e $compFile.".uncompress") {move($compFile,$WORKPATH."/".$date);} 
		else {unlink $compFile;}
    }

    # Convert decompressed files to cfradial format and remove decompressed files
    foreach $decompFile (<KBOX*.uncompress>) {
		print "decompFile = $decompFile ";
		$under_pos = index($decompFile,"_");
		$date = substr($decompFile,$under_pos+1,8);
		print "date = $date\n";
		$command = "$BINPATH/RadxConvert -f ".$decompFile." -outdir TEMP-cfradFiles";
		system($command);
		unlink $decompFile;
		chdir($WORKPATH."/TEMP-cfradFiles/".$date);
		#print "temp cfrad dir = $WORKPATH/TEMP-cfradFiles/$date\n";

		# Interpolate cfradial files to zebra netcdf format, save cfradial files in data.store
		foreach $cfradFile (<cfrad*nc>) {
			print "   cfradFile = $cfradFile\n";
			$command = "$BINPATH/Radx2Grid -params $WORKPATH/Radx2GridParams_kbox -f $cfradFile";
			#print "   command = $command\n";
			system($command);
			unless (-e $CFRADPATH."/".$date) {mkdir $CFRADPATH."/".$date;}
			move($cfradFile,$CFRADPATH."/".$date);
			chdir($WORKPATH."/TEMP-zebFiles/".$date);
			#print "temp zeb dir = $WORKPATH/TEMP-zebFiles/$date\n";

			# Move zebra files to data.store location, create links, rescan kbox platform in zebra
			foreach $zebFile (<kbox.*.nc>)  {
				print "   zebFile = $zebFile\n";
				unless (-e $ZEBPATH."/".$date) {mkdir $ZEBPATH."/".$date;}
				move($zebFile,$ZEBPATH."/".$date);
				chdir($ZEBPATH."/"."links");
				#print "   zeb links dir = $ZEBPATH/links";
				$command = "ln -s ../".$date."/".$zebFile;
				#print "   command = $command\n";
				system($command);
				$command = "/zebra5/bin/dsrescan -file ".$zebFile." kbox";
				#print "   command = $command\n";
				system($command);
			}
			
		}
		
		# Go back to WORKPATH
		chdir($WORKPATH);
    }
    
    # sleep for 10 minutes . . . .
    print "sleeping for 10 minutes . . .\n";
    system("sleep 600");
    
}

exit;
