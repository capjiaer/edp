
# rundc.csh
# scripts  --> link
# config/usr_cfg.tcl usr_proc.tcl usr_extraconst.tcl
# dbs/datain
# dbs/dataout/010_elab dbs/dataout/020_compile dbs/dataout/030_incropt  
# logs/
# rpts/010_elab rpts/020_compile rpts/030_incropt
# work/
# 

#
# Currently only support wlm/dct/dcg, can not support mmmc/upf/scan stitch mode
#
#

if {[file exists $syn_dc(config,workdir)/scripts/dc_procs.tcl]} {
    source -e -v $syn_dc(config,workdir)/scripts/dc_procs.tcl
}

if {[file exists $syn_dc(config,scrpath)/config/dc_cfg.tcl]} {
    source -e -v $syn_dc(config,scrpath)/config/dc_cfg.tcl
}

if {[file exists $syn_dc(config,workdir)/config/usr_cfg.tcl]} {
    source -e -v $syn_dc(config,workdir)/config/usr_cfg.tcl
}


if {[file exists $syn_dc(config,scrpath)/scripts/dc_cfg_check.tcl]} {
    source -e -v $syn_dc(config,scrpath)/scripts/dc_cfg_check.tcl
}


set syn_subdir "config dbs dbs/datain dbs/dataout logs rpts run \
            dbs/dataout/010_elab dbs/dataout/020_compile dbs/dataout/030_incropt \
            rpts/010_elab rpts/020_compile rpts/030_incropt \
            run/tmp"
set usr_files "usr_proc.tcl usr_extra_const.tcl"; #usr_cfg.tcl from flow         
foreach dir $syn_subdir {
    if {![file isdirectory $syn_dc(config,workdir)/$dir]} {
        file mkdir -p $dir
    }
}

foreach usrfile usr_files {
    if {![file exists $syn_dc(config,workdir)/config/$usrfile]} {
        sh touch  $usrfile
    }
}


set syn_dc(workdir) $syn_dc(config,workdir)/run
set syn_dc(tmpdir) $syn_dc(config,workdir)/run/tmp
set syn_dc(cfgdir) $syn_dc(config,workdir)/config
set syn_dc(logsdir) $syn_dc(config,workdir)/logs
set syn_dc(rptsdir) $syn_dc(config,workdir)/rpts
set syn_dc(dbsdir) $syn_dc(config,workdir)/dbs
set syn_dc(dataindir) $syn_dc(config,workdir)/dbs/datain
set syn_dc(dataoutdir) $syn_dc(config,workdir)/dbs/dataout
set syn_dc(dbselabdir) $syn_dc(config,workdir)/dbs/dataout/010_elab
set syn_dc(dbscompiledir) $syn_dc(config,workdir)/dbs/dataout/020_compile
set syn_dc(dbsincroptdir) $syn_dc(config,workdir)/dbs/dataout/030_incropt
set syn_dc(rptselabdir) $syn_dc(config,workdir)/rpts/010_elab
set syn_dc(rptscompiledir) $syn_dc(config,workdir)/rpts/020_compile
set syn_dc(rptsincroptdir) $syn_dc(config,workdir)/rpts/030_incropt

set syn_dc(desname) $syn_dc(config,desname)


#######################################################
# STEP 1: initial setup
#######################################################
puts "\nSYN_DC: Start synthesis: [ecex date +%m\-%d\ %H\:%M]"
echo "\nSYN_DC: Start synthesis: [ecex date +%m\-%d\ %H\:%M]" > $syn_dc(logsdir)/run_time.log

set_host_options -max_core  $syn_dc(flow,cpucores)
report_host_options

#set command_log_file ""

if {[file exists $syn_dc(config,workdir)/scripts/dc_var.tcl]} {
    source -e -v $syn_dc(config,workdir)/scripts/dc_var.tcl
}


#######################################################
# STEP 2: load library
#######################################################
puts "\nDC_SYN: Start load library: [exec date +%m\-%d\ %H\:%M]...\n"

# need lib proc generation, here is temperary method
set syn_dc(all_liblist) [lsort -u [cocat [glob -nocomplain $syn_dc(techlib,stdlib_list)] \
                                [glob -nocomplain $syn_dc(techlib,memlib_list)]  \
                                [glob -nocomplain $syn_dc(techlib,macrolib_list)] \
                ]]
                
# set syn_dc(all_liblist) [get_all_timing_libs -stage syn -pvt ssg0p750vm40c  -rccor cworst_ccworst]

#set libpath ""
#set liblist ""
#foreach onelib $all_liblist {
#    lappend libpath [file dirname $onelib]
#    lappend liblist  [file tail $onelib]
#}
#set search_path  [concat [lsort -u $libpath] $syn_dc(tool,synlib_path) .]
#set target_library [lsort -u $liblist]
#set synthetic_library dw_foundation.sldb
#set link_library "* $target_library $synthetic_library"
#
#if {[shell_is_in_topographical_mode]} {
#    if {$syn_dc(config,dctmwndm)}  { mw_ndm_setup_dct}
#}

syn_dc_lib_setup

puts "\nDC_SYN: load library done: [exec date +%m\-%d\ %H\:%M]...\n"

#######################################################
# STEP 3: load design and link and dataout/rpts written out
#######################################################

syn_dc_load_design

if {$syn_dc(flow,debug_step) eq "link"} {
    if { ![link] } { 
    	puts "\nDC_SYN: please debug unresolve error.\n"
    	return
    }
}
#######################################################
# STEP 4:load constraints in precompile stage --> upf/sdc/saif/def/...
#######################################################

syn_dc_load_design_constraints
syn_dc_load_impl_constraints
syn_dc_load_physical_constraints
if {$syn_dc(flow,debug_step) eq "precompile"} {
    puts "\nDC_SYN: please debug issues in precompile stage.\n"
    return
}
#######################################################
# STEP 5: first compile and dataout/rpts written out
#######################################################
#syn_dc_precompile_check
#syn_dc_first_compile
set compile_args "-scan -gate_clock -no_seq_output_inversion"

if {!$syn_dc(config,auto_boundary)} {
	append compile_args " -no_boundary_optimization"
}

if {!$syn_dc(config,auto_ungroup)} {
	append compile_args " -no_autoungroup"
}

if {!$syn_dc(config,retime)} {
	append compile_args " -retime"
}

if {$syn_dc(config,spg)} {
	append compile_args " -spg"
}

puts "syn_dc_INFO: $compile_args"
eval compile_ultra $compile_args

if {[info exists syn_dc(flow,compile_args)]} {
    append syn_dc(flow,compile_args) "$compile_args"
} else {
    puts "syn_dc_WARN: Can't define the variable syn_dc(flow,compile_args)."
}

syn_dc_compile_dataout_rpts_gen

if {$syn_dc(flow,debug_step) eq "compile"} {
    puts "\nDC_SYN: please debug issues in compile stage.\n"
    return
}

#######################################################
# STEP 6: scan insertion
#######################################################
#
#######################################################
# STEP 7: incr compile and dataout/rpts written out
#######################################################

#syn_dc_incr_compile
if {[file exists $syn_dc(dbscompiledir)/$syn_dc(desname).register_bank.rpt]} {
    source -echo -verbose $syn_dc(dbscompiledir)/$syn_dc(desname).register_bank.rpt
}

if {$syn_dc(config,auto_path_group)} {
    create_auto_path_groups -mode map
}

if {[info exists syn_dc(flow,compile_args)]} {
    append syn_dc(flow,compile_args) " -incremental"
}

if {$syn_dc(flow,incr_num) > 0} {
    for {set n 1} {$n <= $syn_dc(flow,incr_num)} {incr n} {
        eval compile_ultra $incr_cmd
        if {$n == $syn_dc(flow,incr_num)} {
            set syn_dc(config,incr_stage) "final"
        } else {
            set syn_dc(config,incr_stage) "incr_opt${n}"
        }

    if {$syn_dc(config,auto_path_group)} {
        remove_auto_path_groups -mode map
    }

        optimize_netlist -area
    }
# optimize_netlist -area

}

syn_dc_incr_dataout_rpts_gen

if {$syn_dc(flow,debug_step) eq "incrcompile"} {
    puts "\nDC_SYN: please debug issues in incremental compile stage.\n"
    return
}


