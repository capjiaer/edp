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

# 1. CLOCK ROUTING RULES
create_route_type -name top \
	-top_preferred_layer $vars(clock_layer,top_top) -bottom_preferred_layer $vars(clock_layer,top_bottom) \
        -preferred_routing_layer_effort high  -non_default_rule $vars(clock_ndr) 

create_route_type -name trunk \
	-top_preferred_layer $vars(clock_layer,trunk_top) -bottom_preferred_layer $vars(clock_layer,trunk_bottom) \
        -preferred_routing_layer_effort high -non_default_rule $vars(clock_ndr)

create_route_type -name leaf \
	-top_preferred_layer $vars(clock_layer,leaf_top) -bottom_preferred_layer $vars(clock_layer,leaf_bottom) \
        -preferred_routing_layer_effort high -non_default_rule "CLK_1W2S"

set_ccopt_property route_type -net_type top top
set_ccopt_property route_type -net_type leaf leaf
set_ccopt_property route_type -net_type trunk trunk

# 2. SET CCOPT_PROPERTIES: (CLOCK CELL TYPE)
set_ccopt_property inverter_cells     $vars(cts,inverter)
set_ccopt_property buffer_cells       $vars(cts,buffer)
set_ccopt_property clock_gating_cells $vars(cts,clockgating)
set_ccopt_property add_driver_cell    $vars(cts,buffer)
setUsefulSkewMode -noBoundary true -useCells $vars(cts,inverter)

foreach ckg [get_ccopt_property clock_gating_cells] {
   set_dont_touch ${ckg} false
   setDontUse ${ckg} false
}

# TARGET MAX TRANSITION
set_ccopt_property target_max_trans -net_type top 150ps
set_ccopt_property target_max_trans -net_type trunk 150ps
set_ccopt_property target_max_trans -net_type leaf 110ps

# ETC CCOPT PROPERTIES FROM CDNS
set_ccopt_property use_inverters true
set_ccopt_property cell_density 0.80
set_ccopt_property routing_top_min_fanout 2000
set_ccopt_property extract_network_latency true
set_ccopt_property update_io_latency true
set_ccopt_property max_fanout 32
set_ccopt_property auto_limit_insertion_delay_factor 1.4
set_ccopt_property scan_reorder true


set_ccopt_property pro_can_move_datapath_insts true
set_ccopt_property pro_skew_safe_drv_buffering   true;   
set_ccopt_property post_conditioning_enable_drv_fixing_by_rebuffering true; # default false
set_ccopt_property post_conditioning_enable_routing_eco true; # default false
set_ccopt_property post_conditioning_enable_skew_fixing true; # default false
set_ccopt_property post_conditioning_enable_skew_fixing_by_rebuffering true; # default false

foreach ct [get_ccopt_clock_trees *] {
   Puts "   INFO    >> setting max length constraints for clock tree : $ct"
   set_ccopt_property max_source_to_sink_net_length -clock_tree $ct -net_type top 200um
   set_ccopt_property max_source_to_sink_net_length -clock_tree $ct -net_type trunk 200um
   set_ccopt_property max_source_to_sink_net_length -clock_tree $ct -net_type leaf 120um
}


# Extra log output
ccopt_internal_messages -on
# Speed up AAE
setAaeTmpFile -directory ./aae_tmp

# For early clock flow in place_opt
if { $vars(Early_clock_flow) == 1 } {
  setOptMode -usefulSkewTNSPreCTS true
  setVar LS_PLACEOPT::poEarlyClockFlowWNSOptSlackBandMultipler 4.0 ; # If you want more aggresive optimize, increase this value.
}

#3. create/source clock tree spec:
create_ccopt_clock_tree_spec -keep_all_sdc_clocks -filename ./ccopt.spec
source ./ccopt.spec

