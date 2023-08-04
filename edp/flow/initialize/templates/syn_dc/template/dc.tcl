
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

if {[file exists $SYNDC(config,workdir)/scripts/dc_procs.tcl]} {
    source -e -v $SYNDC(config,workdir)/scripts/dc_procs.tcl
}

if {[file exists $SYNDC(config,scrpath)/config/dc_cfg.tcl]} {
    source -e -v $SYNDC(config,scrpath)/config/dc_cfg.tcl
}

if {[file exists $SYNDC(config,workdir)/config/usr_cfg.tcl]} {
    source -e -v $SYNDC(config,workdir)/config/usr_cfg.tcl
}


if {[file exists $SYNDC(config,scrpath)/scripts/dc_cfg_check.tcl]} {
    source -e -v $SYNDC(config,scrpath)/scripts/dc_cfg_check.tcl
}


set syn_subdir "config dbs dbs/datain dbs/dataout logs rpts run \
            dbs/dataout/010_elab dbs/dataout/020_compile dbs/dataout/030_incropt \
            rpts/010_elab rpts/020_compile rpts/030_incropt \
            run/tmp"
set usr_files "usr_proc.tcl usr_extra_const.tcl"; #usr_cfg.tcl from flow         
foreach dir $syn_subdir {
    if {![file isdirectory $SYNDC(config,workdir)/$dir]} {
        file mkdir -p $dir
    }
}

foreach usrfile usr_files {
    if {![file exists $SYNDC(config,workdir)/config/$usrfile]} {
        sh touch  $usrfile
    }
}


set SYNDC(workdir) $SYNDC(config,workdir)/run
set SYNDC(tmpdir) $SYNDC(config,workdir)/run/tmp
set SYNDC(cfgdir) $SYNDC(config,workdir)/config
set SYNDC(logsdir) $SYNDC(config,workdir)/logs
set SYNDC(rptsdir) $SYNDC(config,workdir)/rpts
set SYNDC(dbsdir) $SYNDC(config,workdir)/dbs
set SYNDC(dataindir) $SYNDC(config,workdir)/dbs/datain
set SYNDC(dataoutdir) $SYNDC(config,workdir)/dbs/dataout
set SYNDC(dbselabdir) $SYNDC(config,workdir)/dbs/dataout/010_elab
set SYNDC(dbscompiledir) $SYNDC(config,workdir)/dbs/dataout/020_compile
set SYNDC(dbsincroptdir) $SYNDC(config,workdir)/dbs/dataout/030_incropt
set SYNDC(rptselabdir) $SYNDC(config,workdir)/rpts/010_elab
set SYNDC(rptscompiledir) $SYNDC(config,workdir)/rpts/020_compile
set SYNDC(rptsincroptdir) $SYNDC(config,workdir)/rpts/030_incropt

set SYNDC(desname) $SYNDC(config,desname)


#######################################################
# STEP 1: initial setup
#######################################################
puts "\nSYN_DC: Start synthesis: [ecex date +%m\-%d\ %H\:%M]"
echo "\nSYN_DC: Start synthesis: [ecex date +%m\-%d\ %H\:%M]" > $SYNDC(logsdir)/run_time.log

set_host_options -max_core  $SYNDC(flow,cpucores)
report_host_options

#set command_log_file ""

if {[file exists $SYNDC(config,workdir)/scripts/dc_var.tcl]} {
    source -e -v $SYNDC(config,workdir)/scripts/dc_var.tcl
}


#######################################################
# STEP 2: load library
#######################################################
puts "\nDC_SYN: Start load library: [exec date +%m\-%d\ %H\:%M]...\n"

# need lib proc generation, here is temperary method
set SYNDC(all_liblist) [lsort -u [cocat [glob -nocomplain $SYNDC(techlib,stdlib_list)] \
                                [glob -nocomplain $SYNDC(techlib,memlib_list)]  \
                                [glob -nocomplain $SYNDC(techlib,macrolib_list)] \
                ]]
                
# set SYNDC(all_liblist) [get_all_timing_libs -stage syn -pvt ssg0p750vm40c  -rccor cworst_ccworst]

#set libpath ""
#set liblist ""
#foreach onelib $all_liblist {
#    lappend libpath [file dirname $onelib]
#    lappend liblist  [file tail $onelib]
#}
#set search_path  [concat [lsort -u $libpath] $SYNDC(tool,synlib_path) .]
#set target_library [lsort -u $liblist]
#set synthetic_library dw_foundation.sldb
#set link_library "* $target_library $synthetic_library"
#
#if {[shell_is_in_topographical_mode]} {
#    if {$SYNDC(config,dctmwndm)}  { mw_ndm_setup_dct}
#}

syndc_lib_setup

puts "\nDC_SYN: load library done: [exec date +%m\-%d\ %H\:%M]...\n"

#######################################################
# STEP 3: load design and link and dataout/rpts written out
#######################################################

syndc_load_design

if {$SYNDC(flow,debug_step) eq "link"} {
    if { ![link] } { 
    	puts "\nDC_SYN: please debug unresolve error.\n"
    	return
    }
}
#######################################################
# STEP 4:load constraints in precompile stage --> upf/sdc/saif/def/...
#######################################################

syndc_load_design_constraints
syndc_load_impl_constraints
syndc_load_physical_constraints
if {$SYNDC(flow,debug_step) eq "precompile"} {
    puts "\nDC_SYN: please debug issues in precompile stage.\n"
    return
}
#######################################################
# STEP 5: first compile and dataout/rpts written out
#######################################################
#syndc_precompile_check
#syndc_first_compile
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

puts "SYNDC_INFO: $compile_args"
eval compile_ultra $compile_args

if {[info exists SYNDC(flow,compile_args)]} {
    append SYNDC(flow,compile_args) "$compile_args"
} else {
    puts "SYNDC_WARN: Can't define the variable SYNDC(flow,compile_args)."
}

syndc_compile_dataout_rpts_gen

if {$SYNDC(flow,debug_step) eq "compile"} {
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

#syndc_incr_compile
if {[file exists $SYNDC(dbscompiledir)/$SYNDC(desname).register_bank.rpt]} {
    source -echo -verbose $SYNDC(dbscompiledir)/$SYNDC(desname).register_bank.rpt
}

if {$SYNDC(config,auto_path_group)} {
    create_auto_path_groups -mode map
}

if {[info exists SYNDC(flow,compile_args)]} {
    append SYNDC(flow,compile_args) " -incremental"
}

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
    }
# optimize_netlist -area

}

syndc_incr_dataout_rpts_gen

if {$SYNDC(flow,debug_step) eq "incrcompile"} {
    puts "\nDC_SYN: please debug issues in incremental compile stage.\n"
    return
}


