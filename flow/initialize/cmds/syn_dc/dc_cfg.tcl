

set SYNDC(config,projname) ""
set SYNDC(config,desname) ""
set SYNDC(config,workdir) "[pwd]"
set SYNDC(config,scrpath) ""; # script root path

set SYNDC(config,dataintype) "RTL"; # RTL/MIX/AUTO, RTL only uses vcs -sverilog
# currently support vcs and mix style, auto NOT support
# mix include verilog/sv/vhdl/netlist/db/ddc format based on tcl 
# can cover the following variables in filelist file
# - rtl_search_paths
# - rtl_verilog_files
# - rtl_sverilog_files
# - rtl_vhdl_files
# - netlist_verilog_files
# - netlist_vhdl_files
# - db_files
# - ddc_files
set SYNDC(datain,filelist) ""; # currently follow vcs syntax
set SYNDC(datain,premap_file) ""
set SYNDC(datain,hdl_defines) "SYNTHESIS ASIC"
set SYNDC(config,rtl_pg_flag) "0"


set SYNDC(datain,sdc_file) "$SYNDC(config,workdir)/dbs/datain/$SYNDC(config,desname).sdc"
set SYNDC(datain,upf_file) "$SYNDC(config,workdir)/dbs/datain/$SYNDC(config,desname).upf"
set SYNDC(datain,extra_const_file) "$SYNDC(config,workdir)/config/usr_extra_const.tcl"
set SYNDC(datain,saif_file) ""
set SYNDC(datain,def_file) ""
set SYNDC(datain,fp_file) ""

set SYNDC(techlib,process) "s4"; #t7/t6/t5/t4/s4
#set SYNDC(techlib,cor_name) "ssg0p750vm40c cworst_ccworst";#pvt rc
# need lib proc generation, here is temperary method
set SYNDC(techlib,stdlib_list) "";# absolute path
set SYNDC(techlib,memlib_list) ""
set SYNDC(techlib,macrolib_list) ""
# need lib proc generation
# 
set SYNDC(techlib,dontuse_cell_list) "*/*D16* */*D20*"
set SYNDC(techlib,dontouch_cell_list) ""
set SYNDC(techlib,mwreflibs) ""
set SYNDC(techlib,techfile) ""  
set SYNDC(techlib,mapfile) ""
set SYNDC(techlib,maxtluplus) ""
set SYNDC(techlib,mintluplus) ""
set SYNDC(techlib,tiecell) ""


set SYNDC(tool,version) [get_app_var sh_product_version]
set SYNDC(tool,synlibpath) "/app/eda/synopsys/syn/$SYNDC(tool,version)/libraries/syn"

set SYNDC(flow,optstrategy) "timing"; #timing/power/timing_power/area
set SYNDC(flow,timingeffort) ""
set SYNDC(flow,ungroupdw) "0"
set SYNDC(flow,cpucores) "8"
#set SYNDC(flow,dcstep) ""
set SYNDC(config,enable_scan) "0"
set SYNDC(flow,incr_num) "1"
set SYNDC(flow,compile_args) ""
set SYNDC(config,incr_stage) "final"



set SYNDC(flow,powerana) "0"
set SYNDC(flow,debug_step) "link"; #link/precompile/compile/incrcompile/

set SYNDC(flow,restore_dbs) ""

set SYNDC(config,keep_redundant_regs) "1"

set SYNDC(config,runmode) ""; #wlm,dct
set SYNDC(config,dcnxt) "0"
set SYNDC(config,ndm) "0"
set SYNDC(config,mmmc) "0"
set SYNDC(config,cgposcell) ""
set SYNDC(config,cgnegcell) ""
set SYNDC(config,clock_gating_max_flops) "32"
set SYNDC(config,clock_gating_stages_num) "2"

set SYNDC(config,auto_boundary) ""
set SYNDC(config,auto_ungroup) ""
set SYNDC(config,retime) ""
set SYNDC(config,spg) ""
set SYNDC(config,auto_path_group) "0"

set SYNDC(config,min_route_layer) ""
set SYNDC(config,max_route_layer) ""

#set SYNDC(config,timingffort) "high"
set SYNDC(config,critical_range) "0.2"
#set SYNDC(config,config,keepmapflag) "1"
set SYNDC(config,max_transition) ""
set SYNDC(config,max_capacitance) ""
set SYNDC(config,max_fanout) ""
set SYNDC(config,set_load) ""
set SYNDC(config,driving_cell) ""



# impl constraint file 
set SYNDC(config,dontouchinsts) ""
set SYNDC(config,dontouchnets) ""
set SYNDC(config,sizeonlyinsts) ""
set SYNDC(config,dontcginsts) ""
set SYNDC(config,dontmbinsts) ""
set SYNDC(config,nonscaninsts) ""
set SYNDC(config,keepboundmods) ""
#set SYNDC(config,dftxxxx) ""
#set SYNDC(config,dftxxxx) ""
#set SYNDC(config,dftxxxx) ""
#set SYNDC(config,scandefout) "0"

#set SYNDC(dataout,ddc) ""
#set SYNDC(dataout,pg) ""
#set SYNDC(dataout,) ""



