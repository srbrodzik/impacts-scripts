#!/usr/bin/perl

#use warnings;
#use strict;

$BASE_DIR = "/home/disk/funnel/impacts";
#$CGI_DIR = $BASE_DIR."/cgi-bin";
#$OPS_CGI_DIR = $CGI_DIR."/impacts/ops";
$DATA_DIR = $BASE_DIR."/archive";
$OPS_DATA_DIR = $DATA_DIR."/ops";
$MODEL_DATA_DIR = $DATA_DIR."/model";
$RES_DATA_DIR = $DATA_DIR."/research";
#$DOC_ROOT = "/home/disk/user_www/brodzik/html";
$output_file = $BASE_DIR."/products_hash";
$output_file_new = $BASE_DIR."/products_hash_new";

if (-e $output_file) {
    $command = "/bin/cp ".$output_file." ".$output_file.".bak";
    system($command);
}

open (HASH, '>'.$output_file_new);
#open (DEBUG, '>'."DEBUG.txt");

# Get ops data first

@platforms = ("upper_air",
              "sfc_anal",
              "extrema",
              "totals",
	      
	      "nexrad",
	      "prof_alba",
	      "prof_bell",
	      "prof_bron",
	      "prof_buff",
	      "prof_chaz",
	      "prof_clym",
	      "prof_eham",
	      "prof_jord",
	      "prof_oweg",
	      "prof_quee",
	      "prof_redh",
	      "prof_stat",
	      "prof_ston",
	      "prof_suff",
	      "prof_tupp",
	      "prof_want",
	      "prof_webs",
	      
	      "goes_east",
	      "gpm",
	      "skewt",
	      "wet_bulb",
	      "asos",
	      "nys_ground");
#print "platforms = @platforms\n";
#print "nplatforms = $#platforms\n";
#$num_platforms = $#platforms + 1;
#print "num_platforms = $num_platforms\n";
#@products = (["ir_4km","vis_1km","vis_4km","wv_8km"],
@products = (["850mb","700mb","500mb","300mb","200mb"],
             ["atlantic","n_amer"],
             ["max_temp","min_temp"],
             ["precip24","snow"],
	     ["bgm_bref","bgm_vel","box_bref","box_vel","ccx_bref","ccx_vel","dix_bref","dix_vel","dox_bref","dox_vel","enx_bref","enx_vel","gyx_bref","gyx_vel","okx_bref","okx_vel"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["lidar_cnr","lidar_horiz_ws","lidar_ts","lidar_vert_ws","mwr_integrations","mwr_ts"],
	     ["ir_ch14","vis_ch02","wv_ch08"],
	     ["dpr","gmi"],
	     ["ALB","BUF","CHH","CHS","DTX","GYX","IAD","ILN","ILX","OKX","PIT","RNK","WAL"],
	     ["ALB","BUF","CHH","CHS","DTX","GYX","IAD","ILN","ILX","OKX","PIT","RNK","WAL"],
             #["kalb","kacy","kbos",       "khwv","kbwi",       "kcon",       "kged","khfd","kisp",       "korf","kphl",       "kpwm","kdca","kric","kavp","kwal"],
             #["kalb","kacy","kbos",              "kbwi",       "kcon",       "kged",                     "korf","kphl",       "kpwm","kdca","kric","kavp","kwal"],
	     ["kalb","kacy","kbos","kbgm","kbuf","kbwi","kcmh","kcon","kdtw","kged","khfd","kind","kilx","korf","kphl","kpit","kpwm","kdca","kric","kavp","kwal"],
	     ["ande","bing","brew","broc","buff","elmi","fred","gfal","ilak","malo","nhud","oswe","pots","sara","stat","ston","wate","west"]);
#print "products = @{products[0]}\n";
#print "nproducts = $#(products[0])\n";

for $iplat (0..$#platforms) {
    $plat = $platforms[$iplat];
    #print "plat = $plat\n";
    @prods = @{$products[$iplat]};
    for $iprod (0..$#prods) {
	$prod = $prods[$iprod];
	#print "   prod = $prod\n";

	# go thru date subdirs & check for $prod
	@dates = ();
	$plat_dir = $OPS_DATA_DIR."/".$plat;
	opendir(PLAT_DIR,$plat_dir);
	while ($date = readdir(PLAT_DIR) ) {
	    next if ($date =~ m/^\./);
	    $date_dir = $plat_dir."/".$date;
	    opendir(DATE_DIR,$date_dir);
	    while ($file = readdir(DATE_DIR) ) {
		next if ($file =~ m/^\./);
		($fcategory,$fplatform,$fdate,$fprod) = split(/\./,$file);
		if ($fprod eq $prod) {
		    push(@dates,$date);
		    close(DATE_DIR);
		    last;
		}
	    }
	    $date_dir = "";
	}
	@dates = sort @dates;
	print HASH "$plat:$prod";
	for $i (0..$#dates) {
	    print HASH ":$dates[$i]";
	}
	print HASH "\n";
    }
    closedir(PLAT_DIR);
}

# Get model data next

@platforms = ("wrf_nam_04km",
	      "wrf_nam_12km",
	      "wrf_nam_36km",
	      "wrf_gfs_04km_imp",
	      "wrf_gfs_36km_imp");
#$num_platforms = $#platforms + 1;
#print "num_platforms = $num_platforms\n";
@products = (["01_pcp1","00_winds_sfc"],
	     ["03_pcp3","03_snow3","00_temps_sfc"],
	     ["00_temps_sfc","00_slp_thickness","00_temps_500","00_700_RHomg","03_pcp3","03_snow3"],
	     ["03_pcp3","12_pcp12","00_melt","00_sfc","00_wssfc"],
	     ["03pcp3","12_pcp12","00_300j","00_500vor","00_500temp","00_850t","00_925rh","00_melt","00_sfc","00_wssfc"]);

for $iplat (0..$#platforms) {
    $plat = $platforms[$iplat];
    #print "plat = $plat\n";
    @prods = @{$products[$iplat]};
    for $iprod (0..$#prods) {
	$prod = $prods[$iprod];
	#print "   prod = $prod\n";

	# go thru date subdirs & check for $prod
	@dates = ();
	$plat_dir = $MODEL_DATA_DIR."/".$plat;
	opendir(PLAT_DIR,$plat_dir);
	while ($date = readdir(PLAT_DIR) ) {
	    next if ($date =~ m/^\./);
	    $date_dir = $plat_dir."/".$date;
	    opendir(DATE_DIR,$date_dir);
	    while ($file = readdir(DATE_DIR) ) {
		next if ($file =~ m/^\./);
		($fcategory,$fplatform,$fdate,$fprod) = split(/\./,$file);
		if ($fprod eq $prod) {
		    push(@dates,$date);
		    close(DATE_DIR);
		    last;
		}
	    }
	    $date_dir = "";
	}
	@dates = sort @dates;
	print HASH "$plat:$prod";
	for $i (0..$#dates) {
	    print HASH ":$dates[$i]";
	}
	print HASH "\n";
    }
    closedir(PLAT_DIR);
}

# Get research data next

@platforms = ("er2",
	      "p3",

	      "brookhaven",
	      "manhattan",
	      "southampton",
	      "stonybrook",
	      "stonybrookmobile",

	      "brookhaven",
	      "d3r",
	      "kaspr",
	      "manhattan",
	      "npol",
	      "stonybrook",
	      "stonybrookmobile",

	      "skewt",
	      "text_sounding");
#print "platforms = @platforms\n";
#print "nplatforms = $#platforms\n";
#$num_platforms = $#platforms + 1;
#print "num_platforms = $num_platforms\n";
@products = (["ampr","cpl","crs","cosmir","exrad","flight_track","hiwrap_ka","hiwrap_ku"],
	     ["avaps","cloud_probe","flight_track","phips","tamms","wisper"],

	     ["met_station"],
	     ["met_station","parsivel2"],
	     ["met_station","smartflux_flux","smartflux_met","smartflux_sonic","smartflux_turb"],
	     ["met_station","parsivel2","pluvio","skycam","solar_tracker"],
	     ["met_station"],

	     ["ceil075","dopp_lidar","mrr2"],
	     ["ka_ppi_zdb","ka_rhi_zdb","ku_ppi_rhohv","ku_ppi_vel","ku_ppi_zdb","ku_rhi_rhohv","ku_rhi_vel","ku_rhi_zdb"],
	     ["ppi_dbz","ppi_ldr","ppi_phidp","ppi_rhohv","ppi_rhoxh","ppi_sw","ppi_vel","ppi_veldp","ppi_zdr","rhi_dbz","rhi_ldr","rhi_phidp","rhi_rhohv","rhi_rhoxh","rhi_sw","rhi_vel","rhi_veldp","rhi_zdr","vpt_dbz","vpt_ldr","vpt_sw","vpt_vel"],
	     ["ceil150","ceil150_cirrus","mrr_pro"],
	     ["ppi_cz","ppi_npid","ppi_rhohv","ppi_vr","ppi_zdr","rhi_cz","rhi_npid","rhi_rhohv","rhi_vr","rhi_zdr"],
	     ["mrr_pro","wband_spec_refl","wband_tseries","xband_ph_arr"],
	     ["dopp_lidar","mrr","xband_ph_arr"],

	     ["sbum","uiuc"],
	     ["sbum","uiuc"]);

for $iplat (0..$#platforms) {
    $plat = $platforms[$iplat];

    #print DEBUG "plat = $plat\n";

    @prods = @{$products[$iplat]};
    for $iprod (0..$#prods) {
	$prod = $prods[$iprod];

	#print DEBUG "   prod = $prod\n";

	# go thru date subdirs & check for $prod
	@dates = ();

	#print DEBUG "Top of while loop, dates = @dates\n";

	$plat_dir = $RES_DATA_DIR."/".$plat;

	#print DEBUG "   plat_dir = $plat_dir\n";

	opendir(PLAT_DIR,$plat_dir);
	while ($date = readdir(PLAT_DIR) ) {
	    
	    #print DEBUG "   date = $date\n";

	    next if ($date =~ m/^\./);
	    $date_dir = $plat_dir."/".$date;

	    #print DEBUG "   date_dir = $date_dir\n";

	    opendir(DATE_DIR,$date_dir);
	    while ($file = readdir(DATE_DIR) ) {

		#print DEBUG "   file = $file\n";

		next if ($file =~ m/^\./);
		($fcategory,$fplatform,$fdate,$fprod) = split(/\./,$file);

		#print DEBUG "   fcategory = $fcategory\n";
		#print DEBUG "   fplatform = $fplatform\n";
		#print DEBUG "   fdate     = $fdate\n";
		#print DEBUG "   fprod     = $fprod\n";
		#print DEBUG "   prod      = $prod\n";

		if ($fprod eq $prod) {
		    push(@dates,$date);

		    #print DEBUG "   after push, dates = @dates\n";

		    close(DATE_DIR);
		    last;
		}
	    }
	    $date_dir = "";
	}
	@dates = sort @dates;

	#print DEBUG "   Final dates = @dates\n";

	print HASH "$plat:$prod";
	for $i (0..$#dates) {
	    print HASH ":$dates[$i]";
	}
	print HASH "\n";
    }
    closedir(PLAT_DIR);
}

close(HASH);
#close(DEBUG);

# move new hash file to hash file
$command = "/bin/cp ".$output_file_new." ".$output_file;
system($command);

exit;
