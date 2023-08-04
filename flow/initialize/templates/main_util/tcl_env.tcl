set script_path [file normalize [info script]]
regexp -nocase {(.*cmds)/(.*)} $script_path matched_info flow_path rest_info
set tcl_package [file normalize [file join $flow_path "../flow/packages/tcl/pnr_innovus"]]
set env_tcl [file normalize [file join $flow_path "../config/full.tcl"]]
source "$tcl_package/main.tcl"

lappend auto_path $tcl_package
#package require file_edit_func
#package require data_func

# Initialize finished
source $env_tcl

