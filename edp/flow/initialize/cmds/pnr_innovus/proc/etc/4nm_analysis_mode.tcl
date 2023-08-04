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
# Analsis Mode options
###################################################################################
setAnalysisMode -analysisType onChipVariation -cppr both -usefulSkew true

if { $vars(pocv) == 1 } {
	setLimitedAccessFeature socv 1
	setBetaFeature socv 1
	setAnalysisMode -socv true
	setDelayCalMode -engine aae \
		-accurate_receiver_out_load true \
		-advanced_pincap_mode true \
		-combine_mmmc early_late \
		-enable_high_accuracy_mode true \
		-eng_enableCheckTC true \
		-enable_high_fanout false \
		-equivalent_waveform_model_si_threshold 0.1 \
		-siMode opt_signoff \
		-slewOutBoundLimitHigh 3.40282346638520e+38 \
		-socv_lvf_mode derived_moments \
		-enable_estimate_slew true \
		-enable_quiet_receivers_for_hold true

	if { $step == "route_opt" } { setDelayCalMode -equivalent_waveform_model_propagation true -equivalent_waveform_model_type vivo -SIAware true }

	setSIMode -attacker_alignment timing_aware_edge -enable_logical_correlation true \
          -separate_delta_delay_on_data true -si_reselection slack \
          -accumulated_small_attacker_threshold 10.01 \
          -enable_delay_report true \
          -enable_glitch_report true \
          -individual_attacker_threshold 0.015 \
          -unconstrained_net_use_inf_tw false \
          -delta_delay_annotation_mode lumpedOnNet

	set_global timing_socv_statistical_min_max_mode mean_and_three_sigma_bounded
	set_global timing_enable_spatial_derate_mode true
	set_global timing_derate_spatial_distance_unit 1nm
	set_global timing_set_nsigma_multiplier 3
	set_global timing_enable_backward_compatible_nsigma_multiplier false
	set timing_library_infer_socv_from_aocv true
	set_global timing_report_enable_verbose_ssta_mode true

	set_global report_timing_format {timing_point fanout edge cell slew_mean slew_sigma slew user_derate total_derate load delay_mean delay_sigma delay arrival_mean arrival_sigma arrival }


	###################################################################################
	# Timing Check
	set_global timing_library_infer_cap_range_from_ccs_receiver_model true ; # # To make this compatible with cap range model of PT
	# The following three will actually be default with optimus.
	set_global _timing_enable_parallel_arcs_reduction true 
	set_global _timing_enable_parallel_check_arc_merging true 
	#The below setting is the only SOCV mode that works with IPO
	set_global _timing_mt_end_tag true
	set _timing_enable_first_mt_end_tag true
	set timing_enable_backward_compatible_mt_endtag_mode false
	set_global timing_library_mt_mmmc_flow true
	set_global timing_library_use_pin_voltage_for_ccs_wf true

	###################################################################################
	# PT var
	#- OT:   rc_cache_min_max_rise_fall_ceff TRUE      (Default:false)
	#  INVS: # not same as rc_* var, but avoids nldm pin caps being reported by report_timing in INVS
	set timing_report_use_receiver_model_capacitance true ; 
	set report_precision 4
	set_global timing_cppr_threshold_ps 5

	#set pt_var_arr(1) "timing_remove_clock_reconvergence_pessimism true"
	set_global timing_remove_clock_reconvergence_pessimism true ;	
	#set pt_var_arr(9) "timing_enable_max_capacitance_set_case_analysis true"
	set_global timing_disable_drv_reports_on_constant_nets true
	#set pt_var_arr(10) "timing_early_launch_at_borrowing_latches false"
	#- OT:   timing_enable_max_capacitance_set_case_analysis true      (Default:false)
	set_global timing_use_latch_early_launch_edge true 

	# Configure libs for variation linear adjustment of Hold only (PT)
	# Setup analysis with RSS / Hold analysis with linear sum constraint variation
	set_global timing_library_setup_constraint_corner_sigma_multiplier 0
	set_global timing_library_hold_constraint_corner_sigma_multiplier 3
	set_global timing_library_scale_aocv_to_socv_to_n_sigma 1
	foreach view [all_delay_corners] { set_timing_derate -cell_check -early -sigma 0.0 [get_lib_cells */*] -delay_corner $view }

}

###################################################################################
# ExtractMode
setExtractRCMode -lefTechFileMap $env(INNOVUS_QRCTECH_MAP_FILE)
setExtractRCMode -relative_c_th 0.01 -coupling_c_th 1.0

if { $step == "route_opt" } { setExtractRCMode -effortLevel $vars(extract_effort) ; # medium: tQuantus  | high: iQuantus
} else { setExtractRCMode -effortLevel medium ; # medium: tQuantus  | high: iQuantus 
}

###################################################################################
# Statistical Via
set_global timing_socv_rc_variation_mode true 
setDelayCalMode -eng_enableVoltDepRcSens true 
###################################################################################

