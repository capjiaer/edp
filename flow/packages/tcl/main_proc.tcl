proc get_proc_info {tag flow_path {return_proc_info 1}} {
	# This proc works for deliver required procs for each sub flow.
	set script_path [file normalize [info script]]
	set proc_path [file join $flow_path "packages/tcl" $tag]
	puts "Get proc info from $proc_path"
	set file_list [glob -nocomplain -type f [file join $proc_path *]]
	if {[llength $file_list]} {
		foreach ele $file_list {
			if {$return_proc_info} {
				puts "Read in proc $ele"
			}
			source $ele
		}
	}
}
