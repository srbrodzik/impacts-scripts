#!/usr/bin/python

import os
import shutil

inDir = '/home/disk/funnel/impacts-website/archive/ops/asos'
outDir = '/home/disk/funnel/impacts-website/archive_ncar/surface/ASOS'
category_new = 'surface'
platform_new = 'Meteogram'

# In catalog
'''
asos_sites = {'kacy':'Atlantic_City_NJ',
              'kalb':'Albany_NY',
              'kavp':'Scranton_PA',
              'kbos':'Boston_MA',
              'kbgm':'Binghamton_NY',
              'kbuf':'Buffalo_NY',
              'kbwi':'BWI_Airport_MD',
              'kcmh':'Columbus_OH',
              'kcon':'Concord_NH',
              'kdca':'Reagan_Airport_VA',
              'kdtw':'Detroit_MI',
              'kewr':'Newark_NJ',
              'kged':'Georgetown_DE',
              'khfd':'Hartford_CT',
              'kilx':'Lincoln_IL',
              'kind':'Indianapolis_IN',
              'kisp':'Islip_NY',
              'kjfk':'JFK_Airport_NY',
              'klga':'LaGuardia_Airport_NY',
              'korf':'Norfolk_VA',
              'kphl':'Philadelphia_PA',
              'kpit':'Pittsburgh_PA',
              'kpwm':'Portland_ME',
              'kric':'Richmond_VA',
              'kwal':'Wallops_VA'}

'''
# All sites with images
asos_sites = {'k1v4':'Saint_Johnsbury_VT',
              'kabe':'Allentown_PA',
              'kack':'Nantucket_MA',
              'kacy':'Atlantic_City_NJ',
              'kadg':'Adrian_MI',
              'kafn':'Jaffrey_NH',
              'kagc':'Pittsburgh_Allegheny_PA',
              'kakq':'Wakefield_VA',
              'kakr':'Akron_OH',
              'kalb':'Albany_NY',
              'kanj':'Sault_Ste_Marie_MI',
              'kaoh':'Lima_OH',
              'kaoo':'Altoona_PA',
              'kapn':'Alpena_MI',
              'kart':'Watertown_NY',
              'kaug':'Augusta_ME',
              'kavp':'Scranton_PA',
              'kazo':'Kalamazoo_MI',
              'kbdl':'Bradley_International_CT',
              'kbed':'Bedford_MA',
              'kbeh':'Benton_Harbor_MI',
              'kbfd':'Bradford_PA',
              'kbgm':'Binghamton_NY',
              'kbgr':'Bangor_ME',
              'kbiv':'Holland_MI',
              'kbjj':'Wooster_OH',
              'kbkw':'Beckley_WV',
              'kblf':'Bluefield_WV',
              'kbmg':'Bloomington_IN',
              'kbml':'Berlin_NH',
              'kbos':'Boston_Logan_MA',
              'kbtl':'Battle_Creek_MI',
              'kbtv':'Burlington_VT',
              'kbuf':'Buffalo_NY',
              'kbwg':'Bowling_Green_KY',
              'kbwi':'BWI_International_MD',
              'kcar':'Caribou_ME',
              'kcho':'Charlottesville_VA',
              'kckb':'Clarksburg_WV',
              'kcle':'Cleveland_OH',
              'kcmh':'Columbus_OH',
              'kcmx':'Hancock_MI',
              'kcon':'Concord_NH',
              'kcrw':'Charleston_WV',
              'kdan':'Danville_VA',
              'kdaw':'Rochester_NH',
              'kday':'Dayton_OH',
              'kdca':'Reagan_National_VA',
              'kdet':'Detroit_Coleman_Municipal_MI',
              'kdfi':'Defiance_OH',
              'kdkk':'Dunkirk_NY',
              'kdsv':'Dansville_NY',
              'kdtw':'Detroit_Metropolitan_MI',
              'kduj':'DuBois_PA',
              'kdxr':'Danbury_CT',
              'kdyl':'Doylestown_PA',
              'kekn':'Elkins_WV',
              'kelm':'Elmira_NY',
              'kelz':'Wellsville_NY',
              'keri':'Erie_PA',
              'kevv':'Evansville_IN',
              'kewr':'Newark_International_NJ',
              'kfdy':'Findlay_OH',
              'kfft':'Frankfort_KY',
              'kfig':'Clearfield_PA',
              'kfit':'Fitchburg_MA',
              'kfnt':'Flint_MI',
              'kfrg':'Farmingdale_NY',
              'kfve':'Frenchville_ME',
              'kfwa':'Fort_Wayne_International_IN',
              'kfzy':'Fulton_NY',
              'kged':'Georgetown_DE',
              'kgez':'Shelbyville_IN',
              'kgfl':'Glens_Falls_NY',
              'kgkj':'Meadville_PA',
              'kglr':'Gaylord_MI',
              'kgnr':'Greenville_ME',
              'kgrr':'Grand_Rapids_MI',
              'kgsh':'Goshen_IN',
              'khao':'Hamilton_OH',
              'khfd':'Hartford_CT',
              'khgr':'Hagerstown_MD',
              'khie':'Whitefield_NH',
              'khlg':'Wheeling_WV',
              'khpn':'White_Plains_NY',
              'khtl':'Houghton_Lake_MI',
              'khts':'Huntington_WV',
              'khuf':'Terre_Haute',
              'khul':'Houlton_ME',
              'khzy':'Ashtabula_OH',
              'kiad':'Washington_Dulles_International_VA',
              'kiag':'Niagara_Falls_NY',
              'kijd':'Willimantic_CT',
              'kilg':'Wilmington_DE',
              'kiln':'Wilmington_Air_Park_OH',
              'kilx':'Lincoln_IL',        # not defined on site; check
              'kimt':'Iron_Mountain_MI',
              'kind':'Indianapolis_International_IN',
              'kipt':'Williamsport_PA',
              'kisp':'Islip_Airport_NY',
              'kiwi':'Wiscasset_ME',
              'kizg':'Fryeburg_ME',
              'kjfk':'JFK_International_NY',
              'kjkl':'Jackson_KY',
              'kjst':'Johnstown_PA',
              'kjxn':'Jackson_MI',
              'klaf':'Lafayette_IN',
              'klan':'Lansing_MI',
              'kleb':'Lebanon_NH',
              'klex':'Lexington_KY',
              'klga':'LaGuardia_Airport_NY',
              'klhq':'Lancaster_OH',
              'klns':'Lancaster_PA',
              'kloz':'London_KY',
              'klpr':'Lorain_OH',
              'klyh':'Lynchburg_VA',
              'kmbs':'Saginaw_International_MI',
              'kmdt':'Harrisburg_International_PA',
              'kmfd':'Mansfield_OH',
              'kmgj':'Montgomery_NY',
              'kmgw':'Morganstown_WV',
              'kmgy':'Dayton_OH',
              'kmht':'Manchester_NH',
              'kmie':'Muncie_IN',
              'kmiv':'Millville_NJ',
              'kmkg':'Muskegon_MI',
              'kmlt':'Millinocket_ME',
              'kmmk':'Meriden_CT',
              'kmnn':'Marion_OH',
              'kmpv':'Montpelier_VT',
              'kmrb':'Martinsburg_WV',
              'kmss':'Massena_NY',
              'kmtp':'Montauk_Airport_NY',
              'kmvl':'Morrisville_VT',
              'kmvy':'Marthas_Vineyard_MA',
              'kore':'Orange_MA',
              'korf':'Norfolk_VA',
              'korh':'Worcester_MA',
              'koxb':'Ocean_City_MD',
              'kp58':'Port_Hope_MI',
              'kp59':'Copper_Harbor_MI',
              'kpah':'Paducah_KY',
              'kpbg':'Plattsburgh_NY',
              'kpeo':'Penn_Yan_NY',
              'kphd':'New_Philadelphia_OH',
              'kphf':'Newport_News_VA',
              'kphl':'Philadelphia_International_PA',
              'kpit':'Pittsburgh_International_PA',
              'kpkb':'Parkersburg_WV',
              'kpln':'Pellston_MI',
              'kpou':'Poughkeepsie_NY',
              'kpsf':'Pittsfield_MA',
              'kptk':'Pontiac_MI',
              'kptw':'Pottstown_PA',
              'kpwm':'Portland_ME',
              'krdg':'Reading_PA',
              'kric':'Richmond_International_VA',
              'krme':'Rome_NY',
              'kroa':'Roanoke_VA',
              'kroc':'Rochester_NY',
              'ksbn':'South_Bend_IN',
              'ksby':'Salisbury_MD',
              'ksdf':'Louisville_International_KY',
              'kseg':'Selinsgrove_PA',
              'kslk':'Saranac_Lake_NY',
              'ksmq':'Somerville_NJ',
              'ksyr':'Syracuse_Airport_NY',
              'ktdz':'Toledo_OH',
              'kthv':'York_PA',
              'ktol':'Toledo_OH',
              'kttn':'Trenton_NJ',
              'ktvc':'Traverse_City_MI',
              'kvpz':'Valparaiso_IN',
              'kvsf':'Springfield_VT',
              'kvta':'Newark_OH',
              'kwal':'Wallops_FF_VA',
              'kyng':'Youngstown_OH',
              'kzzv':'Zanesville_OH'}

for date in os.listdir(inDir):
    print(date)
    if not os.path.isdir(outDir+'/'+date):
        os.mkdir(outDir+'/'+date)
    for file in os.listdir(inDir+'/'+date):
        if 'asos' in file:
            #print(file)
            basename = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            (category,platform,datetime,site) = basename.split('.')
            try:
                file_new = category_new+'.'+platform_new+'.'+datetime+'.ASOS_'+asos_sites[site]+ext
                #print(file_new)
                shutil.copy(inDir+'/'+date+'/'+file,outDir+'/'+date+'/'+file_new)
            except:
                print(file+': '+site+' not in dict')



            
# For testing
'''
import os
indir = '/home/disk/funnel/impacts-website/archive/ops/asos/20200111'
siteList = []
for file in os.listdir(indir):
    basename = os.path.splitext(file)[0]
    (category,platform,datetime,site) = basename.split('.')
    if not site in siteList:
        siteList.append(site)
siteList = sorted(siteList)
'''
