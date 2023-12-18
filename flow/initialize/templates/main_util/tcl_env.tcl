set script_path [file normalize [info script]]
regexp -nocase {(.*cmds)/(.*)} $script_path matched_info cmds_path rest_info
set main_path [file dirname $cmds_path]
set tool_info [file tail [file dirname $script_path]]
set tcl_package [file normalize [file join $flow_path "../flow/packages/tcl/$tool_info"]]
set env_tcl [file normalize [file join $main_path "config/full.tcl"]]
source [file dirname $tcl_package]/main_proc.tcl
lappend auto_path $tcl_package
# Initialize finished
source $env_tcl

