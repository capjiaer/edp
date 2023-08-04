

proc infoexist {} {

    

}

proc syndc_mw_ndm_setup {} {

    global SYNDC


    if {[shell_is_in_topographical_mode]} {
    
        if {[shell_is_dcnxt_shell]} {
            if {$SYNDC(config,ndm)} {
                set ndm_flag 1
            } else {
                set ndm_flag 0
            }
        } else {
            set ndm_flag 0
        }
        if {!$ndm_flag} {
            set mw_reference_library $SYNDC(techlib,mwreflibs)
            set mw_design_library $SYNDC(tmpdir)/$SYNDC(config,desname).mw
        
            if {[file exists $mw_design_library]} {
                file delet -force $mw_design_library
            }
        
            extend_mw_layers
        
            create_mw_lib \
                -technology $SYNDC(techlib,techfile) \
                -mw_reference_library $mw_reference_library \
                $mw_design_library
            open_mw_lib $mw_design_library
        
            check_library

            if {!$SYNDC(config,mmmc)} {
                set_tlu_plus_files  -max_tluplus $SYNDC(techlib,maxtluplus) \
                                    -min_tluplus $SYNDC(techlib,mintluplus) \
                                    -tech2itf_map $SYNDC(techlib,mapfile)
                
                check_tlu_plus_files
            }
        } else {
        
        	if {[file isdirectory $SYNDC(dbsdir)/$SYNDC(config,desname).dlib]} {
        		file delete -force $SYNDC(dbsdir)/$SYNDC(config,desname).dlib
        	}
            
        #	create_lib $dbsdir/$SYNDC(config,desname).dlib -technology $SYNDC(techlib,techfile) -ref_libs [get_ndm_files]
        #    open_lib $dbsdir/$SYNDC(config,desname).dlib
        
        
         #   check_library
            
        }
}

proc syndc_lib_setup {} {

global SYNDC search_path target_library link_library

    set libpath ""
    set liblist ""
    foreach onelib $SYNDC(all_liblist) {
        lappend libpath [file dirname $onelib]
        lappend liblist  [file tail $onelib]
    }
    set search_path  [concat [lsort -u $libpath] $SYNDC(tool,synlib_path) .]
    set target_library [lsort -u $liblist]
    set synthetic_library dw_foundation.sldb
    set link_library "* $target_library $synthetic_library"

    syndc_mw_ndm_setup 

} 

proc syndc_dont_use_cell {} {

    global SYNDC

    if {[llength $SYNDC(techlib,dontuse_cell)] ==0} {
        puts "DC_Warning: Can not find dont use cell."
    }
    
    set dont_use_list [list ]
    foreach lib_cell $SYNDC(techlib,dontuse_cell_list) {
        lappend dont_use_list [get_object_name [get_lib_cells $lib_cell -q]]
    }
    set_dont_use $dont_use_list 
    set_dont_use $dont_use_list -power 
 #   foreach libcell_spec $SYNDC(techlib,dontuse_cell) {
 #       set lib_spec [file dirname $libcell_spec]
 #       set cell_spec [file tail $libcell_spec]
 #       regsub -all {\*} $lib_spec {.*} lib_spec
 #       
 #       foreach_in_collection lib [get_libs] {
 #           set libname [get_attribute $lib name]
 #           if {[regexp $lib_spec $libname]} {
 #               set lib_cells [get_lib_cells $libname/$cell_spec -q]
 #               foreach_in_collection lib_cell $lib_cells {
 #                   set lib_cell_name [get_object_name $lib_cell]
 #                   set_dont_use $lib_cell_name
 #                   set_dont_use $lib_cell_name -power
 #               }
 #           }
 #       }
    
	#foreach dont_use $SYNDC(dontuse_cells) {
	#	set_dont_use [get_lib_cells */$dont_use]
	#	set_dont_use [get_lib_cells */$dont_use] -power
	#}
    #}
}

proc syndc_dataout_generic {} {
    global SYNDC
    
    write -hierarchy -format ddc -output $SYNDC(dbselabdir)/$SYNDC(desname).ddc
    write_file -format verilog -output $SYNDC(dbselabdir)/$SYNDC(desname).v 
    exec gzip -f $SYNDC(dbselabdir)/$SYNDC(desname).v
    redirect -compress -tee $SYNDC(rptselabdir)/$SYNDC(desname).qor.rpt {report_qor}

}

proc syndc_load_design {} {

    global SYNDC search_path

    set svf_files [glob -nocomplain $SYNDC(dbsdir)/*.svf]
    if {[file exists $svf_files]} {
        foreach svf_file $svf_files {
            file delete -force $svf_file
        }
    }
    set_svf $SYNDC(dbsdir)/$SYNDC(desname).svf
    set_vsdc $SYNDC(dbsdir)/$SYNDC(desname).vsdc
    
    set_app_var hdlin_infer_multibit default_all
    set_app_var hdlin_enable_hier_map true
    set_app_var compile_seqmap_identify_shift_registers false
    set_app_var hdlin_enable_rtldrc_info true
    
    define_design_lib WORK -path ./WORK
    
    if {$SYNDC(flow,powerana)} {
        saif_map -start
    }


# analyze -define $SYNDC(datain,hdl_defines) -f sverilog -lib WORK -vcs "-f ./data/SynRtl/SynRtl.vf

	if {![info exists syndc(datain,hdl_defines)] || ($SYNDC(datain,hdl_defines) eq "")} {
    	set syndc(datain,hdl_defines) ""
    }

    if {$SYNDC(config,dataintype) == "RTL"} {

	    set syndc(datain,hdl_defines) [join [concat $SYNDC(datain,hdl_defines)] "+"]
	    if {[info exists syndc(datain,filelist)] && [file exists $SYNDC(datain,filelist)]} {
	    	if {[info exists syndc(datain,hdl_defines)] && $SYNDC(datain,hdl_defines) ne ""} {
	    		analyze -format sverilog -vcs "-f ${syndc(datain,filelist)} +define+$SYNDC(datain,hdl_defines)"
	    	} else {
	    		analyze -format sverilog -vcs "-f $SYNDC(datain,filelist)"
	    	}
        }
    }

    if {$SYNDC(config,dataintype) == "MIX"} {
        source -e -v $SYNDC(datain,filelist)

        if {[info exists rtl_search_paths]} {
            set search_path [concat $rtl_search_paths $search_path]
        }

        # verilog 
        if {[info exists rtl_verilog_files] && $rtl_verilog_files != ""} {
            set readcmd "analyze -format verilog"

            if {$SYNDC(datain,hdl_defines) != ""} {
                set readcmd "$readcmd -define \{ $SYNDC(datain,hdl_defines) \}"
            }

            set readcmd "$readcmd \$rtl_verilog_files"
            eval $readcmd

        }
 
        # sverilog 
        if {[info exists rtl_sverilog_files] && $rtl_sverilog_files != ""} {
            set readcmd "analyze -format sverilog"

            if {$SYNDC(datain,hdl_defines) != ""} {
                set readcmd "$readcmd -define \{ $SYNDC(datain,hdl_defines) \}"
            }

            set readcmd "$readcmd \$rtl_sverilog_files"
            eval $readcmd

        }

        # vhdl 
        if {[info exists rtl_vhdl_files] && $rtl_vhdl_files != ""} {
            set readcmd "analyze -format vhdl"

            if {$SYNDC(datain,hdl_defines) != ""} {
                set readcmd "$readcmd -define \{ $SYNDC(datain,hdl_defines) \}"
            }

            set readcmd "$readcmd \$rtl_vhdl_files"
            eval $readcmd

        }

        # netlist verilog 
        if {[info exists netlist_verilog_files] && $netlist_verilog_files != ""} {
            read_verilog -netlist $netlist_verilog_files
        }

        # netlist vhdl 
        if {[info exists netlist_vhdl_files] && $netlist_vhdl_files != ""} {
            read_vhdl -netlist $netlist_vhdl_files
        }

#        # db file 
#        if {[info exists db_files] && $db_files != ""} {
#            read_vhdl -netlist $db_files
#        }
#
#        # ddc file 
#        if {[info exists ddc_files] && $ddc_files != ""} {
#            read_vhdl -netlist $ddc_files
#        }
        
    }

        # db file 
        if {[info exists db_files] && $db_files != ""} {
            read_vhdl -netlist $db_files
        }

        # ddc file 
        if {[info exists ddc_files] && $ddc_files != ""} {
            read_vhdl -netlist $ddc_files
        }


    if {[info exists syndc(datain,premapfile)] && [file exists $SYNDC(datain,premapfile)]} {
        analyze -format verilog -lib WORK $SYNDC(datain,premapfile)
    }

    elaborate $SYNDC(config,desname)
    #puts "\nDC_SYN: load design done: $TIME_START : [exec date +%m\-%d\ %H\:%M]...\n"

    current_design  $SYNDC(config,desname)
    redirect -file $SYNDC(logsdir)/link.log { link }
   

    #if { ![link] } { 
    #	puts "\nDC_SYN: please debug unresolve error.\n"
    #	return
    #}
    
    #if { ![check_design] } { 
    #	puts "\nDC_SYN:  and please debug check design error.\n"
    #	return
    #}
    
    set_verification_top
    
    puts "\nDC_SYN: link and check design done: $TIME_START : [exec date +%m\-%d\ %H\:%M]...\n"

    set_app_var uniquify_naming_style "$SYNDC(desname)_%s_%d"
    uniquify -force
     
    change_name -rules verilog -hierarchy
    
    syndc_dataout_generic

}

if {0} {
proc syndc_debug_item {step} {

    global SYNDC

    if {$SYNDC(flow,debug_step) eq "link"} {
        if { ![link] } { 
        	puts "\nDC_SYN: please debug unresolve error.\n"
        	return
        }
    }

    if {$SYNDC(flow,debug_step) eq "precompile"} {
        puts "\nDC_SYN: please debug issues in precompile stage.\n"
        return
    }

    if {$SYNDC(flow,debug_step) eq "compile"} {
        puts "\nDC_SYN: please debug issues in compile stage.\n"
        return
    }

    if {$SYNDC(flow,debug_step) eq "incrcompile"} {
        puts "\nDC_SYN: please debug issues in incremental compile stage.\n"
        return
    }
}
}

proc syndc_load_design_constraints {} {

    global SYNDC

    set_fix_multiple_port_nets -all -buffer_constants
    set compile_advanced_fix_multiple_port_nets true

    # load saif
#    if {[info exists design(saif_file)] && [file exists $SYNDC(saif_file)]} {
#		if {[info exists design(saif_inst)] && ($SYNDC(saif_inst) ne "")} {
#			append design(read_saif_map) " -instance $SYNDC(saif_inst) "
#		}
#		eval read_saif -auto_map_names -input $SYNDC(saif_file) $SYNDC(read_saif_args) -verbose
#		report_saif -hier -rtl_saif 
#		report_saif -hier -rtl_saif -missing > $SYNDC(rptsdir)/$SYNDC(desname).missing_saif.rpt
#	}
		

	# load upf
	if {[info exists syndc(datain,upf_file)] && $SYNDC(datain,upf_file) ne ""} {
		if {[file exists $SYNDC(datain,upf_file)]} {
			load_upf $SYNDC(datain,upf_file)
		} else {
        }
	}


	# read sdc
	if {[info exists syndc(datain,sdc_file)] && $SYNDC(datain,sdc_file) ne ""} {
		if {[file exists $SYNDC(datain,sdc_file)]} {
			redirect -file $SYNDC(logsdir)/read_sdc_file.log {source -e -v $SYNDC(datain,sdc_file)}
		} else {
        }
	}

    # cost group setting
	set ports_clock_root [filter_collection [get_attribute [get_clocks] sources] object_class==port]
	group_path -name reg2out -to [all_outputs]
	group_path -name in2reg -from [remove_from_collection [all_inputs] $ports_clock_root]
	group_path -name in2out -from [remove_from_collection [all_inputs] $ports_clock_root] -to [all_outputs]
		

    # critical range
    set_critical_range $SYNDC(config,critical_range) [current_design]
    
    # dont use cell
    syndc_dont_use_cell

    if {[shell_is_in_topographical_mode]} {
    # AHFS 
        set_ahfs_options -enable_port_punching true -preserve_boundary_phase true -no_port_punching [get_cells * -filter "is_hierarchical == true"]
        report_ahfs_options
    }

    set_max_area 0
    
	# max transition/capacitance/fanout
    set_max_transition $SYNDC(config,max_transition) [current_design]
    set_max_capacitance $SYNDC(config,max_capacitance) [current_design]
	set_max_fanout $SYNDC(config,max_fanout) [current_design]
     
    # set load, driving cell
    set_load $SYNDC(config,set_load)
    #set_driving_cell ??

    # load user extra constraints, include cost group
	if {[info exists syndc(datain,extra_const_file)] && $SYNDC(datain,extra_const_file) ne ""} {
		if {[file exists $SYNDC(datain,extra_const_file)]} {
			redirect -file $SYNDC(logsdir)/read_extra_const_file.log {source -e -v $SYNDC(datain,extra_const_file)}
		} else {
        }
	}

    # pocv setting,

	# keep rtl mapped cells
	if {[info exists SYNDC(config,keep_rtl_mapped_cell)] && ($SYNDC(config,keep_rtl_mapped_cell)==1)} {
		puts "preserve rtl mapped cells"
		set mapped_cells [get_flat_cells -quiet -filter "is_mapped==true && ref_name != **logic_1** && ref_name != **logic_0**"]
		if {[sizeof_collection $mapped_cells]>0} {
			set_size_only $mapped_cells -all_instances 
		}
	}

    # ICG style
    set SYNDC(config,cts_clock_gating_cells) [concat $SYNDC(config,cgposcell) $SYNDC(config,cgnegcell)]
    if {[llength $SYNDC(config,cts_clock_gating_cells)] > 0} {
	    foreach cts_clock_gating_cell $SYNDC(config,cts_clock_gating_cells) {
	    	remove_attribute [get_lib_cells */$cts_clock_gating_cell] dont_use
	    	remove_attribute [get_lib_cells */$cts_clock_gating_cell] dont_touch
	    	remove_attribute [get_lib_cells */$cts_clock_gating_cell] pwr_cg_dont_use
	    }
    }

	set_clock_gating_style \
		-num_stages $SYNDC(clock_gating_stages_num) \
		-minmum_bitwidth 4 \
		-max_fanout $SYNDC(clock_gating_max_flops) \
		-control_point before \
		-positive_edge_logic "integrated:$SYNDC(config,cgposcell)" \
		-negative_edge_clock "integrated:$SYNDC(config,cgnegcell)"

#	set_clock_gate_latency -clock [get_clocks] -stage 0 -fanout_latency [list 1-inf 0]
#	set_clock_gate_latency -clock [get_clocks] -stage 1 -fanout_latency [list 1-inf -$SYNDC(cg_adjust_value)]

	# RTL multibit inference banking
	#if {[info exists syndc(rtl_mb_flop)] && ($SYNDC(rtl_mb_flop)==1)} {
		set_multibit_options -mode timing_driven -execute_registers_with_timing_exception true
	#}

	# for multi-Vth design, set the following threthod votage group in library
	set_attribute [get_libs *_ulvt*] default_threshod_voltage_group ulvt -type string
	set_attribute [get_libs *_lvt*] default_threshod_voltage_group lvt -type string
	#set_attribute [get_libs *_svt*] default_threshod_voltage_group svt -type string
	set_attribute [get_libs *_rvt*] default_threshod_voltage_group rvt -type string
	#set_attribute [get_libs *_hvt*] default_threshod_voltage_group hvt -type string
    #set_multi_vth_constraint

	if {[shell_is_in_topographical_mode]} {
		set_congestion_option -mx_util 0.90
	}

# check consistency 
	check_design -summary
	check_design > $SYNDC(dbselabdir)/$SYNDC(desname).check_design.rpt
	check_timing > $SYNDC(dbselabdir)/$SYNDC(desname).check_timing.rpt

	# MB register report pre-compile_ultra 
	redirect -compress -tee $SYNDC(dbscompiledir)/$SYNDC(desname).multibit.hier.rpt {report_multibit -hierarchical}


}

proc syndc_load_impl_constraints {} {
    global SYNDC

}


proc syndc_load_physical_constraints {} {

    global SYNDC


    if {[shell_is_in_topographical_mode]} {
    	#set TIME_START [exec date +%m\-%d\ %H\:%M]
    
    	# specify ignored layers for routing to improve correclation
    	if {$SYNDC(config,min_route_layer) != ""} {
    		set_ignored_layers -min_routing_layer "M[expr $SYNDC(config,min_route_layer) -1]"
    	}
    	if {$SYNDC(config,max_route_layer) != ""} {
    		set_ignored_layers -max_routing_layer "M[expr $SYNDC(config,max_route_layer) -1]"
    	}
    	report_ignored_layers
    	if {[info exists syndc(def_file)] && [file exists $SYNDC(def_file)]} {
    		 extract_physical_constraints -allow_physical_cells $SYNDC(def_file)
    	}
    	if {[info exists syndc(fp_file)] && [file exists $SYNDC(fp_file)]} {
    		read_floorplan  $SYNDC(fp_file)
    	}
    
    	write_floorplan -all $SYNDC(dbscompiledir)/$SYNDC(desname).initial.fp 
    
    	report_physical_constraints > $SYNDC(dbscompiledir)/$SYNDC(desname).physical_constraint.rpt 
        
    	if {![file exists $SYNDC(def_file)] && ![file exists $SYNDC(fp_file)]} {
    		puts "\nDC_SYN: There is no either DEF or Floor-plan file for physical info. Please check\n"
    	}
}

if {0} {
proc syndc_first_compile {} {

    global SYNDC

	set compile_args "-scan -gate_clock -no_seq_output_inversion"
    
	if {!$SYNDC(config,auto_boundary)} {
		append compile_args " -no_boundary_optimization"
	}

	if {!$SYNDC(config,auto_ungroup)} {
		append compile_args " -no_autoungroup"
	}

	if {!$SYNDC(config,retime)} {
		append compile_args " -retime"
	}

	if {$SYNDC(config,spg)} {
		append compile_args " -spg"
	}
 
	puts "SYN_DC: $compile_args"
	eval compile_ultra $compile_args

    if {[info exists SYNDC(flow,compile_args)]} {
        append SYNDC(flow,compile_args) " $compile_args"
    } else {
        puts "SYNDC_WARN: Can't define the variable SYNDC(flow,compile_args)."
    }

    syndc_compile_dataout_rpts_gen

 }
}

proc syndc_compile_dataout_rpts_gen {} {

    global SYNDC

#    saif_map -type primepower -write_map /$SYNDC(desname).for_ptpx.saif_map
#	saif_map  -write_map /$SYNDC(desname)..saif_map 

    set_app_var uniquify_naming_style "$SYNDC(desname)_%s_%d"
    uniquify -force     
    change_name -rules verilog -hierarchy

    write_file -format verilog -hierarchy -output $SYNDC(dbscompiledir)/$SYNDC(desname).v 
	exec gzip -f $SYNDC(dbscompiledir)/$SYNDC(desname).v
    write_file -format ddc -hierarchy -output $SYNDC(dbscompiledir)/$SYNDC(desname).ddc    

	if {[info exists SYNDC(enable_phymb)] && ($SYNDC(enable_phymb)==1) && [shell_is_in_topographical_mode]} {
		# MB merge based on physical location
		set dont_mb_flops [get_flat_cells -filter "remove_multibit==true"]
		if {[sizeof_collection $dont_mb_flops]>0} {
			identify_register_banks -exclude_size_only_flops -exclude_instance [get_flat_cells -filter "remove_multibit==true"] -output $SYNDC(dbscompiledir)/$SYNDC(desname).register_bank.rpt
	    } else {
		    identify_register_banks -exclude_size_only_flops -output $SYNDC(dbscompiledir)/$SYNDC(desname).register_bank.rpt
        }
    }

    redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).clock_gating.ept {report_clock_gating -nosplit}
	redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).ungated_ff.rpt {report_clock_gating -ungated}
	redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).threshold_voltage.rpt {report_threshold_voltage_group }
	redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).check_timing.rpt {check_timing}

	if {[info exists design(saif_file)] && [file exists $design(saif_file)]} {
	#	write_saif -output ./$SYNDC(desname).syn.saif 
	}

    redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).area.rpt {report_area}

    if {$SYNDC(config,mmmc)} {
    } else {
    
    redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).report_constraint.total.rpt {report_constraint -all_violators -nosplit}
    redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).report_constraint.setup.rpt {report_constraint -all_violators -max_delay -nosplit}
    redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).report_power.rpt {report_power}
    }

    redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).qor.rpt {report_qor}

    if {$SYNDC(config,mmmc)} {
    } else {
        if {[shell_is_in_topographical_mode]} {
            redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).report_timing.rpt {report_timing -physical -nets -trans -cap -input -delay_type max -max_paths 200 -nworst 1 -nosplit}
        } else {
            redirect -file $SYNDC(dbscompiledir)/$SYNDC(desname).report_timing.rpt {report_timing  -nets -trans -cap -input -delay_type max -max_paths 200 -nworst 1 -nosplit}
        }
    }

#	foreach clk_one [get_object_name [all_clocks]] {
#	   report_timing -group $clk_one -nets -input -cap -trans -nos -max_paths 200 -nworst 1 > $REPORT_PATH/${TOP_MODULE}_pre_incr_${clk_one}_timing.rpt
#	}

    if {[shell_is_in_topographical_mode]} {
		write_def -output $SYNDC(dbscompiledir)/$SYNDC(desname).def
	}

	foreach fl [glob $SYNDC(dbscompiledir)/*] {
		if {![regexp {\.gz$} $fl] && ![file isdirectory $fl]} {
			exec gzip -f $fl -q
		}
	}
    
    
}

if {0} {
proc syndc_incr_compile {} {

    global SYNDC

    if {[file exists $SYNDC(dbscompiledir)/$SYNDC(desname).register_bank.rpt]} {
        source -echo -verbose $SYNDC(dbscompiledir)/$SYNDC(desname).register_bank.rpt
    }

    if {$SYNDC(config,auto_path_group)} {
        create_auto_path_groups -mode map
    }

    append SYNDC(flow,compile_args) " -incremental"

    if {$SYNDC(flow,incr_num) > 0} {
        for {set n 1} {$n <= $SYNDC(flow,incr_num)} {incr n} {
            eval compile_ultra $incr_cmd
            if {$n == $SYNDC(flow,incr_num)} {
                set SYNDC(config,incr_stage) "final"
            } else {
                set SYNDC(config,incr_stage) "incr_opt${n}"
            }

        if {$SYNDC(config,auto_path_group)} {
            remove_auto_path_groups -mode map
        }

            optimize_netlist -area

            syndc_incr_dataout_rpts_gen
        }
#    optimize_netlist -area

    }
}
}


proc syndc_incr_dataout_rpts_gen {} {

    global SYNDC

    set optrptsdir $SYNDC(rptsincroptdir)/$SYNDC(config,incr_stage)
    set optdbsdir $SYNDC(dbsincroptdir)/$SYNDC(config,incr_stage)

    if {![file isdirectory $optrptsdir]} {
        file mkdir -p $optrptsdir
    }

    if {![file isdirectory $optdbsdir]} {
        file mkdir -p $optdbsdir
    }
     

    uniquify -force -dont_skip_empty_designs

	define_name_rules verilog -preserve_struct_ports
	change_names -rules verilog -hierarchy -log_changes $optrptsdir/$SYNDC(desname).save_design.change_name.rpt

#	define_name_rules ungroup_separateor -map {{"/", "____"}, {",,", "_MB_"}} -preserve_struct_ports
#	change_names -rules ungroup_separateor -hierarchy -log_changes $optrptsdir/$SYNDC(desname).ungroup_and_MB.change_name.rpt

    
    write_file -format verilog -hierarchy -output $optrptsdir/$SYNDC(desname).v

	if {[info exists SYNDC(datain,upf_file)] && $SYNDC(datain,upf_file) ne ""} {
		write_file -format verilog -hierarchy -output  -pg $optrptsdir/$SYNDC(desname).pg.v
		exec gzip -f $optrptsdir/$SYNDC(desname).pg.v
	} 

	if {[shell_is_in_topographical_mode]} {
		create_block_abstraction
	}

	write_file -format ddc -hierarchy -output $optdbsdir/$SYNDC(desname).ddc 

	set_svf -off
	set_vsdc -off 

    if {[shell_is_in_topographical_mode]} {
		write_def -output $optdbsdir/$SYNDC(desname).def
		exec gzip -f  $optdbsdir/$SYNDC(desname).def
        write_floorplan -all $optrptsdir/$SYNDC(desname).fp
	}

	if {$SYNDC(config,enable_scan)} {
		write_scandef -output $optdbsdir/$SYNDC(desname).scan.def
        write_test_model -format ctl -output $optdbsdir/$SYNDC(desname).ctl
	}

	if {[shell_is_in_topographical_mode]} {
		set_app_var write_sdc_output_lumped_net_capacitance false
		set_app_var wrtie_sdc_output_net_resistance false

        if {$SYNDC(config,mmmc)} {
            #write_parasitics -output $optdbsdir/$SYNDC(desname)_${scenario}.syn.spef
            #write_sdf $optdbsdir/$SYNDC(desname)_${scenario}.syn.sdf
		    #set all_active_scenario_saved [all_active_scenarios]
		    #set current_scenario_saved [current_scenario]
		    #all_active_scenarios -all
		    #foreach scenario [all_active_scenarios] {
		    #	current_scenario $scenario 
		    #	write_sdc -nosplit $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc 
		    #	sh sed -i '/^set_operating_condition/d' $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc
		    #	sh sed -i '/^set_max_transition/d' $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc
		    #	sh sed -i '/^set_clock_uncertainty/d' $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc
		    #	sh sed -i '/^group_path/d' $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc
		    #	sh sed -i '/^set_timing_derate/d' $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc
		    #	sh sed -i '/^set_ideal_network/d' $optdbsdir/$SYNDC(desname).syn_${scenario}.sdc
		    #	
		    #}
		    #current_scenario $current_scenario_saved
		    #set_active_scenario $all_active_scenario_saved
        } else {
            write_parasitics -output $optdbsdir/$SYNDC(desname).syn.spef
			write_sdf $optdbsdir/$SYNDC(desname).syn.sdf 
			write_sdc -nosplit $optdbsdir/$SYNDC(desname).syn.sdc 
			sh sed -i '/^set_operating_condition/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^set_max_transition/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^set_max_capacitance/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^set_max_fanout/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^set_clock_uncertainty/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^group_path/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^set_timing_derate/d' $optdbsdir/$SYNDC(desname).syn.sdc
			sh sed -i '/^set_ideal_network/d' $optdbsdir/$SYNDC(desname).syn.sdc
	    }
    }


	write_link_library -out $optrptsdir/$SYNDC(desname).link_library.tcl

#	saif_map -type primepower -write_map $optdbsdir/$SYNDC(desname).for_ptpx.saif_map 
#	saif_map -write_map $optdbsdir/$SYNDC(desname).saif_map 
#
#	if {[info exists design(saif_file)] && [file exists $design(saif_file)]} {
#		write_saif -output $optdbsdir/$SYNDC(desname).syn.saif
#	}

    if {[info exists SYNDC(datain,upf_file)] && $SYNDC(datain,upf_file) ne ""} {
		if {[shell_is_in_topographical_mode]} {
    
        } 
    }

    report_qor > $optrptsdir/$SYNDC(desname).qor.rpt

	if {[shell_is_in_topographical_mode]} {
        if {$SYNDC(config,mmmc)} {
	#	    report_timing -scenario [all_active_scenarios] -transition_time -nets -attributes -nosplit -max_paths 200 -sort_by_slack > $optrptsdir/$SYNDC(desname).timing.rpt 
        } else {
		    report_timing -transition_time -nets -attributes -nosplit -max_paths 200 -sort_by_slack > $optrptsdir/$SYNDC(desname).timing.rpt 

	    } 
    } else {
		report_timing  -transition_time -nets -attributes -nosplit -max_paths 200 -sort_by_slack > $optrptsdir/$SYNDC(desname).timing.rpt 
	}

		file mkdir $optrptsdir/timing_rpt 
		foreach group [get_object_name [get_path_group]] {
			set rename_group [regsub -all {/} $group]
			if {[shell_is_in_topographical_mode]} {
                if {$SYNDC(config,mmmc)} {
				#    report_timing -scenario [all_active_scenarios] -transition_time -nets -input_pins -nosplit -max_paths 100 -derate -group $group > $optrptsdir/timing_rpt/$SYNDC(desname).timing.${rename_group}
                } else {
				    report_timing -transition_time -nets -input_pins -nosplit -max_paths 100 -derate -group $group > $optrptsdir/timing_rpt/$SYNDC(desname).timing.${rename_group}
                }
			} else {
				report_timing -transition_time -nets -input_pins -nosplit -max_paths 100 -derate -group $group > $optrptsdir/timing_rpt/$SYNDC(desname).timing.${rename_group}

			}
		}

	if {[shell_is_in_topographical_mode]} {
		report_area -physical -nosplit > $optrptsdir/$SYNDC(desname).area.rpt
		report_area -physical -hierarchy -nosplit > $optrptsdir/$SYNDC(desname).hier.area.rpt
	} else {
		report_area  -nosplit > $optrptsdir/$SYNDC(desname).area.rpt
		report_area  -hierarchy -nosplit > $optrptsdir/$SYNDC(desname).hier.area.rpt
	}

    report_design > $optrptsdir/$SYNDC(desname).report_design.rpt
	report_area -designware > $optrptsdir/$SYNDC(desname).dw_area.rpt
	#report_area -hierarchy > $optrptsdir/$SYNDC(desname).hier_area.rpt
	report_resources -hierarchy -nosplit > $optrptsdir/$SYNDC(desname).report_resources.rpt

    if {$SYNDC(config,mmmc)} {
    } else {
        report_constraint -all_violators -nosplit > $optrptsdir/$SYNDC(desname).all_vios.rpt
        report_constraint -all_violators -max_delay -nosplit > $optrptsdir/$SYNDC(desname).
	    report_clock_gating -nosplit > $optrptsdir/$SYNDC(desname).clock_gating.rpt
	    report_clock_gating -ungated > $optrptsdir/$SYNDC(desname).clock_ungating.rpt
	    report_threshold_voltage_group > $optrptsdir/$SYNDC(desname).threshold_voltage_group.rpt
    }

	redirect -file $optrptsdir/$SYNDC(desname).multibit.bangking.rpt {report_multibit_banking -nosplit}

	if {[shell_is_in_topographical_mode]} {
        if {$SYNDC(config,mmmc)} {
		#    report_power -scenario [all_active_scenarios] -nosplit > $optrptsdir/$SYNDC(desname).report_power.rpt
        } else {
		    report_power -nosplit > $optrptsdir/$SYNDC(desname).report_power.rpt
        }
	} else {
		report_power -nosplit > $optrptsdir/$SYNDC(desname).report_power.rpt
	}

	# report_transformed_registers

	if {[shell_is_in_topographical_mode] && ([info exists SYNDC(config,report_congestion)] && ($SYNDC(config,report_congestion)==1))} {
		# report_congestion (topo mode only) uses zroute for estimating and reporting routing related congestion which improve the congestion correlation with ICC
		# DCT supports create_route_guide to be consistent with ICC 

		report_congestion > $optrptsdir/$SYNDC(desname).congestion.rpt 
    }
}



