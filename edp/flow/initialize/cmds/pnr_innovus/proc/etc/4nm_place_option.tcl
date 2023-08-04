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

####################################################################
# 4nm_placement option
####################################################################
setDesignMode -powerEffort $vars(power_effort)

setPlaceMode -placeIOPins true
setPlaceMode -place_detail_swap_eeq_cells true
setPlaceMode -pinTrackSnappingForNonDPTLayer true
setPlaceMode -place_global_ignore_scan false
setPlaceMode -place_global_exp_allow_missing_scan_chain true

setPlaceMode -place_detail_max_shifter_depth 25
setPlaceMode -place_detail_allow_border_pin_abut true
setPlaceMode -place_global_cong_effort high
setPlaceMode -place_global_routing_blockage_aware true
setPlaceMode -place_global_module_aware_spare true
setPlaceMode -viaInPin true
#setPlaceMode -place_global_clock_gate_aware false -place_global_clock_power_driven true -place_global_clock_power_driven_effort high  ; # design specific
setPlaceMode -place_detail_check_route true -place_detail_check_cut_spacing true

## For 1cpp filler
setPlaceMode -place_detail_legalization_inst_gap 1 

set_interactive_constraint_modes [all_constraint_modes -active]
set_max_fanout 32 [current_design]

# Trialroute mode
setTrialRouteMode -reset
setRouteMode -earlyGlobalHonorClockSpecNDR true
setRouteMode -earlyGlobalMinRouteLayer $vars(min_route_layer)
setRouteMode -earlyGlobalMaxRouteLayer $vars(max_route_layer)

#==== setNanoRouteMode
setNanoRouteMode -drouteHonorAlternativeTrackColor "M1"

####################################################################
# 4nm setOptMode
####################################################################
setOptMode -reset
setOptMode -fixFanoutLoad true
setOptMode -honorFence true
setOptMode -fixHoldAllowSetupTnsDegrade false
setOptMode -maxLength 450 -postRouteAreaReclaim holdAndSetupAware -verbose true
setOptMode -reclaimRestructuringEffort high
setOptMode -resizeShifterAndIsoInsts true  ; # LVLU resize control
setOptMode -drcMargin -0.2  ; # consider -0.2  (will help area/pwr)
setOptMode -fixSISlew true

setIlmMode -keepHighFanoutPorts true -keepLoopBack false -keepFlatten true 
setUsefulSkewMode -allNegEndPoints true 
setUsefulSkewMode -maxAllowedDelay 1000 
setUsefulSkewMode -maxSkew true 

# exp. optMode settings
setOptMode -expExtremeCongestionAwareBuffering true -expReclaimEffort high ;

setPlaceMode -RTCSpread false

# Multibit FF opt
if { $vars(Mbit_opt) ==1 } {
  setLimitedAccessFeature FlipFlopMergeAndSplit 1
  setOptMode -multiBitFlopOpt true -multiBitFlopOptIgnoreSDC false \
             -flopMergeConstScanChain true -powerDrivenMBFFOpt true -flopMergeDebug true
  setPlaceMode -mergeDualFlops true
}

