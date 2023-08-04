#################################################################################################
##                                                                                             ##
## SAMSUNG FOUNDRY RESERVES THE RIGHT TO CHANGE PRODUCTS, INFORMATION AND SPECIFICATIONS       ##
## WITHOUT NOTICE.                                                                             ##
##                                                                                             ##
## No part of this publication may be reproduced, stored in a retrieval system, or transmitted ##
## in any form or by any means, electric or mechanical, by photocopying, recording,            ##
## or otherwise, without the prior written consent of Samsung. This publication is intended    ##
## for use by designated recipients only. This publication contains confidential information   ##
## (including trade secrets) of Samsung protected by Competition Law, Trade Secrets Protection ##
## Act and other related laws, and therefore may not be, in part or in whole, directly or      ##
## indirectly publicized, distributed, photocopied or used (including in a posting on the      ##
## Internet where unspecified access is possible) by any unauthorized third party. Samsung     ##
## reserves its right to take any and all measures both in equity and law available to it and  ##
## claim full damages against any party that misappropriates Samsung's trade secrets and/or    ##
## confidential information                                                                    ##
##                                                                                             ##
## All brand names, trademarks and registered trademarks belong to their respective owners.    ##
##                                                                                             ##
## 2023 Samsung Foundry                                                                        ##
##                                                                                             ##
#################################################################################################
##                                                                                             ##
## Title                : Samsung_Foundry_LN04LPP_SFDK_PnR_Methodology_Innovus_REV1.01         ##
## Process              : LN04LPP                                                              ##
## Author               : JongHwan Park                                                        ##
## Initial Release Date : January. 31, 2023                                                    ##
## Last Update Date     : January. 31, 2023                                                    ##
## Script Version       : REV1.01                                                              ##
## Usage                : make route_opt                                                       ##
## Tool Version         : Innovus 21.15_s110_1_G or later      	  	                       ##
##                                                                                             ##
#################################################################################################


###################################################################################
# create_analysis_mode
###################################################################################

# get all view corner from user_design.tcl 
set viewList [lsort -unique [concat $pnr_innovus(prects,setup) $pnr_innovus(prects,hold) $pnr_innovus(cts,setup) $pnr_innovus(cts,hold) $vars(postcts,setup) $pnr_innovus(postcts,hold)]]


foreach View $viewList {
	puts "Create view $View"

        if { [regexp {(.*)_(.*)_(.*)_(.*)_(.*_.*)} $View] } { regexp {(.*)_(.*)_(.*)_(.*)_(.*_.*)} $View match v_mode v_corner v_vop v_temp v_rc
	} else { regexp {(.*)_(.*)_(.*)_(.*)_(.*)} $View match v_mode v_corner v_vop v_temp v_rc }
	set V_RC [string toupper $v_rc]
	regsub {m} $v_temp {-} temperature
	regsub {c} $temperature {} temperature

	# Create Library Set
    # modified by chenanping 20230330, sram lvs added
    set std_lvf [glob $env(DK_SOURCE)/stdcell/timing_lvf/*flk*${v_corner}*${v_vop}*${v_temp}*lvf_dth.lib*]
    set rams_lvf [glob $env(DK_SOURCE)/rams/timing/*${v_corner}*${v_vop}*${v_temp}*lvf_dth.lib*]
	create_library_set -name ${v_corner}_${v_vop}_${v_temp} -timing [concat $std_lvf $rams_lvf] 
	# -timing [glob $env(DK_SOURCE)/stdcell/timing_lvf/*flk*${v_corner}*${v_vop}*${v_temp}*lvf_dth.lib*]
		

	# Create RC Corner
	create_rc_corner -name rc_${v_rc}_${v_temp} \
	   -preRoute_res 1\
	   -postRoute_res {1 1 1}\
	   -preRoute_cap 1\
	   -postRoute_cap {1 1 1}\
	   -postRoute_xcap {1 1 1}\
	   -preRoute_clkres 0\
	   -preRoute_clkcap 0\
	   -postRoute_clkcap {1 1 1}\
	   -postRoute_clkres {1 1 1}\
	   -T $temperature\
	   -qx_tech_file $env(INNOVUS_QRCTECH_$V_RC)

	# Create delay corner
	create_delay_corner -name dc_${v_corner}_${v_vop}_${v_temp}_${v_rc} \
	   -library_set ${v_corner}_${v_vop}_${v_temp} \
	   -rc_corner rc_${v_rc}_${v_temp}

	# Create Mode
	create_constraint_mode -name mode_${v_mode}_${v_vop} -sdc $vars(sdc_${v_mode},${v_vop})

	# Create View
	create_analysis_view -name $View -constraint_mode mode_${v_mode}_${v_vop} -delay_corner dc_${v_corner}_${v_vop}_${v_temp}_${v_rc}

}

###################################################################################
# set_analysis_view
##################################################################################

set_analysis_view -setup $vars(prects,setup) -hold $vars(prects,hold)
