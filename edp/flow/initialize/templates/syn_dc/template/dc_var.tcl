
set hdlin_check_no_latch true
set hdlin_enable_hier_map true

set verilogout_no_tri true

if {$SYNDC(config,rtl_pg_flag)} {
    set dc_allow_rtl_pg true
}

set compile_seqmap_propagate_constants false
set compile_delete_unload_sequential_cells false

set case_analysis_with_logic_constants true

set compile_disable_hierarchical_inverter_opt true
set enable_recovery_removal_arcs true

set collection_result_display_limit -1

set compile_seqmap_identify_shift_registers false
set compile_seqmap_identify_shift_registers_with_synchronous_logic false


# need add more variables

	# define pin name synonyms
    if {[regexp {^s} $SYNDC(techlib,process)} {
	    set_pin_name_synonym D next_state
	    set_pin_name_synonym CK clocked_on 
	    set_pin_name_synonym CN clear
	    set_pin_name_synonym SN preset         
    } 
    if {[regexp {^t} $SYNDC(techlib,process)} {
	    set_pin_name_synonym D next_state
	    set_pin_name_synonym CP clocked_on 
	    set_pin_name_synonym CDN clear
	    set_pin_name_synonym SDN preset 
    }
	report_pin_name_synonym

	set_app_var uniquify_naming_style "$SYNDC(desname)_%s_%d"
	#set_app_var bus_naming_style %s_%d; # maybe impact syncell  
    #
    set_app_var power_cg_cell_naming_style "synopsys_clock_gate_%d"

	set_app_var alib_library_analysis_path ./alib

	set_app_var hdlin_enable_upf_compatible_naming true
	set_app_var hdlin_sv_union_member_naming true
	set_app_var report_default_significant_digits 4
	set_app_var timing_separate_clock_gating_group true

	if {[info exits syndc(datain,upffile)] && ($SYNDC(datain,upffile) ne "")} {
		if {[file exists $SYNDC(datain,upffile)]} {
			set_app_var upf_create_implicit_supply_sets true
		} 
	} else {
		set_app_var upf_create_implicit_supply_sets false 
	}

    set_app_var auto_insert_level_shifters_on_clocks all
	set_app_var spg_enable_via_resistance_support true

	set check_error_list [concat OPT-1413 TIM-209 VER-540 VER-1 ELAB-364 ELAB-369 LBR-1 LINT-64 LINT-69 LINT-6 LINT-4 OPT-150 PSYN-415]


	if {[shell_is_in_topographical_mode]} {
#		set_app_var timing_pocvm_enable_analysis true 
	}

	set_app_var enable_recovery_removal_arcs true

	set_app_var timing_check_defaults "clock_no_period generated_clock loops no_input_delay unconstrained_endpoints pulse_clock_cell_type no_driving_cell partial_input_delay data_check_no_clock"
 
	#set_cost_priority -delay

    if { $SYNDC(flow,optstrategy) eq "timing"} {
		if {[shell_is_in_topographical_mode]} {
			set_app_var compile_timing_high_effort true
			set_app_var psynopt_tns_high_effort true
			set_app_var placer_tns_driven true 
		}

		set_app_var power_cg_physically_aware_cg  true
		set_app_var compile_timing_high_effort_tns true
		set_app_var compile_enhanced_tns_optimization_in_incremental true
		set_app_var compile_enhanced_tns_optimization_effort_level medium
	} 

    # coarse placement 
		if {[shell_is_in_topographical_mode]} {
			set_app_var placer_max_cell_density_threshold 0.75
		}

		#  optimizer area in incr
		set_app_var compile_optimize_netlist_area_in_incremental true

		# enable congestion-driven placement in incr compile to improve congestion
		if {[shell_is_in_topographical_mode]} {
			set_app_var spg_congestion_placement_in_incremental_compile true 
		}
	

	# disable register inversion
	set_app_var compile_seqmap_enable_output_inversion false
    
	 if {[info exists syndc(flow,ungroupdw)] && !$SYNDC(flow,ungroupdw)} {
		set_app_var compile_ultra_ungroup_dw false 
	 }

	 # wait for DW license
	 set_app_var synlib_wait_for_design_license [list DesignWare]

	 # inference of MB from bus defined in rtl
	 set_app_var hdlin_infer_multibit default_all 

	 if {[info exits syndc(config,keep_redundant_regs)] && ($SYNDC(config,keep_redundant_regs) == 1)} {
		set_app_var compile_delete_unloaded_sequential_cell false
		set_app_var compile_seqmap_propagate_constant false
	 }

 # set_app_var enable_register_transformation_log true

     #file normalize $SYNDC(datain,upf_file) 
     if {[info exists SYNDC(datain,upf_file)] && [file exists $SYNDC(datain,upf_file)]}
        set_app_var hdlin_enable_upf_compatible_naming true
     }

