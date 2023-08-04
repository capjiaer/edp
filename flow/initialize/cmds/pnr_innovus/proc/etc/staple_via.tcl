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

if { [dbGet top.pgNets.sVias.userClass post_staple] != "0x0"  } {
  deselectAll
  editSelectVia -subClass post_staple
  deleteSelectedFromFPlan
  deselectAll
}

setViaGenMode -reset
setViaGenMode -use_cce 1
setViaGenMode -genvia_naming_prefix genvia_staple
setViaGenMode -optimize_cross_via true -keep_existing_via 1; # 0: replacing, 1: keep both, 2: keep original
setViaGenMode -hookup_via_style loose 

set M2Distance 3
set M2Pitch [dbGet [dbGet -p  head.layers.name M2].pitchX]
set power_staple_distance [expr $M2Distance * $M2Pitch]
setViaGenMode -hookup_via_distance $power_staple_distance
setViaGenMode -hookup_via_min_distance $power_staple_distance

setViaGenMode -respect_signal_routes 1 -respect_stdcell_geometry 1

setViaGenMode -reset -cutclass_preference
setViaGenMode -reset -viarule_preference
setViaGenMode -ignore_viarule_enclosure false


# 1st staple via insertion (M2 FAT type)
if { $vars(TRACK) == "6P25TR" } {
setViaGenMode -viarule_preference { V1_15_1_8_73_HV V2_8_73_28_0_VH }}
if { $vars(TRACK) == "7P94TR" } {
setViaGenMode -viarule_preference { V1_15_1_8_100_HV V2_8_100_28_0_VH }}

setViaGenMode -preferred_vias_only open
setViaGenMode -hookup_loose_runtime 1
setNanoRouteMode -drouteCutMaxSpacingCheckEffort 0
setViaGenMode -area_only 0
editPowerVia -add_vias 1 -orthogonal_only 0 -bottom_layer M1 -top_layer M3 -uda post_staple

## Fix SMAC violation
set iter  0
while {1} {
  clearDrc
  verify_drc -limit -1 -layer_range {M1 M3}

  set count 0
  set checkDrc { "Same Metal Aligned Cuts" "Same_Metal_Aligned_Cuts" }
  foreach drc $checkDrc {
     foreach drc_box [dbShape [dbGet -e [dbGet -p top.markers.subType $drc].box]] {
        set drc_box_new [dbShape $drc_box SIZEX 0.100 SIZEY 0.008]        
        deselectAll
        select_obj [dbGet -e -p [dbQuery -objType sViaInst -area $drc_box_new].userClass post_staple]
        select_obj [dbGet -e -p [dbQuery -objType sViaInst -area $drc_box_new].userClass STRIPE_M2]
        set count [expr $count + [llength [dbGet -e selected]]]
        editDelete -selected
     }
  }
  puts "Staple via deletion($iter): $count"
  if {$count==0} {break}
  incr iter
}
