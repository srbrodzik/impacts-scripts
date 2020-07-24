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

@platforms = ("extrema",
	      "noaa",
	      "sfc_anal",
	      "sfc_metar",
              "totals",
	      "upper_air",
    
	      "nexrad",
	      "nys_lidar_cnr",
	      "nys_lidar_horz_wspd",
	      "nys_lidar_vert_wspd",
	      "nys_mwr_cloud",
	      "nys_mwr_ts",
	      
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
@products = (["max_temp","min_temp"],
	     ["day1_psnow_gt_04","day2_psnow_gt_04","day3_psnow_gt_04","lowtrack","snow_precip_24hr"],
	     ["atlantic","n_amer"],
	     ["mid_atlantic","mid_west","northeast"],
	     ["precip24","snow"],
	     ["850mb","700mb_fronto","700mb","500mb","300mb","200mb"],
    
	     ["akq_bref","akq_vel","bgm_bref","bgm_vel","box_bref","box_vel","ccx_bref","ccx_vel","cle_bref","cle_vel","dix_bref","dix_vel",
	      "dox_bref","dox_vel","dtx_bref","dtx_vel","dvn_bref","dvn_vel","enx_bref","enx_vel","grb_bref","grb_vel","grr_bref","grr_vel",
	      "gyx_bref","gyx_vel","iln_bref","iln_vel","ilx_bref","ilx_vel","ind_bref","ind_vel","iwx_bref","iwx_vel","lot_bref","lot_vel",
	      "lwx_bref","lwx_vel","mhx_bref","mhx_vel","mkx_bref","mkx_vel","okx_bref","okx_vel","rax_bref","rax_vel","tyx_bref","tyx_vel",
              "vwx_bref","vwx_vel"],
	     ["alba","bell","bron","buff","chaz","clym","eham","jord","oweg","quee","redh","stat","ston","suff","tupp","want","webs"],
	     ["alba","bell","bron","buff","chaz","clym","eham","jord","oweg","quee","redh","stat","ston","suff","tupp","want","webs"],
	     ["alba","bell","bron","buff","chaz","clym","eham","jord","oweg","quee","redh","stat","ston","suff","tupp","want","webs"],
	     ["alba","bell","bron","buff","chaz","clym","eham","jord","oweg","quee","redh","stat","ston","suff","tupp","want","webs"],
	     ["alba","bell","bron","buff","chaz","clym","eham","jord","oweg","quee","redh","stat","ston","suff","tupp","want","webs"],
	     
	     #["ir_ch14","vis_ch02","wv_ch08","ir_4km","vis_4km","wv_4km"],
	     ["multi_ch_color","vis_ch02","ir_4km","vis_4km","wv_4km","M1color","M2color"],
	     ["2Ku","gmi"],
	     ["ALB","APX","BUF","CHH","CHS","DTX","DVN","GRB","GSO","GYX","IAD","ILN","ILX","MHX","MPX","OKX","PIT","RNK","WAL"],
	     ["ALB","APX","BUF","CHH","CHS","DTX","DVN","GRB","GSO","GYX","IAD","ILN","ILX","MHX","MPX","OKX","PIT","RNK","WAL"],
             #["kalb","kacy","kbos",       "khwv","kbwi",       "kcon",       "kged","khfd","kisp",       "korf","kphl",       "kpwm","kdca","kric","kavp","kwal"],
             #["kalb","kacy","kbos",              "kbwi",       "kcon",       "kged",                     "korf","kphl",       "kpwm","kdca","kric","kavp","kwal"],
	     #["kalb","kacy","kbos","kbgm","kbuf","kbwi","kcmh","kcon","kdtw",       "kged","khfd","kind","kilx",                     "korf","kphl","kpit","kpwm","kdca","kric","kavp","kwal"],
	     ["kalb","kacy","kbos","kbgm","kbuf","kbwi","kcmh","kcon","kdtw","kewr","kged","khfd","kind","kilx","kisp","kjfk","klga","korf","kphl","kpit","kpwm","kdca","kric","kavp","kwal"],
	     ["ande","bing","brew","broc","buff","elmi","fred","gfld","gfal","ilak","malo","nhud","oswe","pots","redf","sara","stat","ston","wate","west"]);
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

@platforms = ("wrf_gfs_04km",
	      "wrf_gfs_12km",
	      "wrf_gfs_36km",
	      "gfs_28km",
	      "nam_12km",
	      "hrrr_03km",
	      "hrrr_01km");
#$num_platforms = $#platforms + 1;
#print "num_platforms = $num_platforms\n";
@products = (["00_500_avo","00_700_dBZfronto","00_850_dBZfronto","00_refl_10cm","00_temps_sfc","03_pcp3"],
	     ["00_500_avo","00_700_dBZfronto","00_850_dBZfronto","00_refl_10cm","00_temps_sfc","03_pcp3"],
	     ["00_500_avo","00_700_dBZfronto","00_850_dBZfronto","00_refl_10cm","00_temps_sfc","03_pcp3"],
	     ["00_T2m_us","00_uv250_us","00_z500_vort_us","00_temp_adv_fgen_700_us","00_T850_us","06_ir_us","06_ref_frzn_us"],
	     ["00_T2m_us","00_uv250_us","00_z500_vort_us","00_temp_adv_fgen_700_us","00_T850_us","06_ref_frzn_us"],
	     ["00_T2m_us","00_ir_us","01_ref_frzn_us"],
	     ["00_ctop","00_cref_sfc","00_G114bt_sat","00_lcc_sfc","00_mcc_sfc","00_hcc_sfc","00_wind_250","00_temp_700","00_temp_850","00_temp_925"]);

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

	      "manhattan",
	      "stonybrook",
	      "stonybrookmobile",
	      "ualbany",

	      "brookhaven",
	      "d3r",
	      "kaspr",
	      "manhattan",
	      "npol",
	      "stonybrook",
	      "stonybrookmobile",
	      "ualbany",

	      "skewt");
#print "platforms = @platforms\n";
#print "nplatforms = $#platforms\n";
#$num_platforms = $#platforms + 1;
#print "num_platforms = $num_platforms\n";
@products = (["ampr","cpl_355nm","cpl_532nm","cpl_1064nm","cpl_combo","cpl_aerosol_od","cpl_cloud_od","cpl_column_od","cpl_depol_ratio","cpl_extinction_coef","cpl_feature_type","cpl_iwc","crs","crs_dbz","crs_ldr","crs_sw","crs_vel","cosmir_aft_conical","cosmir_along_track","cosmir_cross_track","cosmir_forward_conical","exrad","exrad_dbz","exrad_sw","exrad_vel","flight_track","hiwrap_ka","hiwrap_Ka_dbz","hiwrap_Ka_sw","hiwrap_Ka_vel","hiwrap_ku","hiwrap_Ku_dbz","hiwrap_Ku_sw","hiwrap_Ku_vel"],
	     ["2DS_distributions","2DS_images","avaps","dropsonde","FCDP_distributions","flight_track","HVPS3A_distributions","HVPS3A_images","phips_camera_C1","phips_camera_C2","tamms","wisper"],

	     ["parsivel"],
	     ["pluvio","solar_tracker"],
	     ["met_station","parsivel"],
	     ["parsivel"],

	     ["ceil075","dopp_lidar","mrr2"],
	     ["ka_ppi_zdb","ka_rhi_zdb","ku_ppi_rhohv","ku_ppi_vel","ku_ppi_zdb","ku_rhi_rhohv","ku_rhi_vel","ku_rhi_zdb"],
	     ["ppi_dbz","ppi_ldr","ppi_phidp","ppi_rhohv","ppi_rhoxh","ppi_sw","ppi_vel","ppi_veldp","ppi_zdr","rhi_dbz","rhi_ldr","rhi_phidp","rhi_rhohv","rhi_rhoxh","rhi_sw","rhi_vel","rhi_veldp","rhi_zdr","vpt_dbz","vpt_ldr","vpt_sw","vpt_vel"],
	     ["ceil150","mrr_pro"],
	     
	     ["ppi_dbz","ppi_hid","ppi_rainr","ppi_rhohv","ppi_vel","ppi_zdr","rhi_dbz","rhi_hid","rhi_rainr","rhi_rhohv","rhi_vel","rhi_zdr"],

	     #["mwr","roger","wband_spec_refl","wband_tseries","xband_ph_arr"],
	     ["roger_spectrum_refl","roger_time_ht","skyler_ppi","skyler_rhi"],
	     ["ceil150","mrr_pro","xband_ph_arr"],
	     ["mrr","mrr_cfad","mrr_parsivel_tseries"],

	     ["NCSU","SBU","UIUC_Mobile_Sonde"]);

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
